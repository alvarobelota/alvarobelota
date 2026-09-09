"""Busca periódica de passagens em oferta e alerta via Telegram.

Uso:
    python -m flightdeals.main
"""

from datetime import date

from flightdeals.config import load_settings
from flightdeals.notifier import TelegramNotifier
from flightdeals.state import deal_key, load_seen, save_seen
from flightdeals.travelpayouts import TravelpayoutsClient


def months_between(start: date, end: date) -> list[date]:
    months = []
    current = start.replace(day=1)
    while current <= end:
        months.append(current)
        if current.month == 12:
            current = current.replace(year=current.year + 1, month=1)
        else:
            current = current.replace(month=current.month + 1)
    return months


def run() -> None:
    settings = load_settings()
    client = TravelpayoutsClient(settings.travelpayouts_token)
    notifier = TelegramNotifier(settings.telegram_bot_token, settings.telegram_chat_id)
    seen = load_seen()

    found_deals = []

    for destination in settings.destinations:
        for month in months_between(settings.date_start, settings.date_end):
            try:
                entries = client.month_matrix(
                    origin=settings.origin,
                    destination=destination.code,
                    month=month,
                    currency=settings.currency,
                    one_way=settings.one_way,
                )
            except Exception as exc:
                print(f"Erro consultando {settings.origin}->{destination.code} em {month}: {exc}")
                continue

            for entry in entries:
                depart_date = entry.get("depart_date")
                return_date = entry.get("return_date")
                price = entry.get("value")
                if depart_date is None or price is None:
                    continue
                if not (settings.date_start.isoformat() <= depart_date <= settings.date_end.isoformat()):
                    continue
                if price > destination.price_threshold_brl:
                    continue

                key = deal_key(destination.code, depart_date, return_date, price)
                if key in seen:
                    continue

                seen.add(key)
                found_deals.append({
                    "destination": destination,
                    "depart_date": depart_date,
                    "return_date": return_date,
                    "price": price,
                })

    if found_deals:
        for deal in found_deals:
            dest = deal["destination"]
            msg_lines = [
                f"✈️ *Oferta encontrada: {settings.origin} → {dest.name} ({dest.code})*",
                f"Ida: {deal['depart_date']}",
            ]
            if deal["return_date"]:
                msg_lines.append(f"Volta: {deal['return_date']}")
            msg_lines.append(f"Preço: {deal['price']} {settings.currency.upper()}")
            notifier.send("\n".join(msg_lines))
        save_seen(seen)
        print(f"{len(found_deals)} oferta(s) nova(s) encontrada(s) e notificada(s).")
    else:
        print("Nenhuma oferta nova dentro do critério desta vez.")


if __name__ == "__main__":
    run()
