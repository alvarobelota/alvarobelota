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


def cheapest_in_range(entries: list[dict], date_start: date, date_end: date) -> dict | None:
    """Entre os trechos retornados, acha o mais barato com partida dentro do range."""
    candidates = [
        e for e in entries
        if e.get("depart_date") and e.get("value") is not None
        and date_start.isoformat() <= e["depart_date"] <= date_end.isoformat()
    ]
    if not candidates:
        return None
    return min(candidates, key=lambda e: e["value"])


def run() -> None:
    settings = load_settings()
    client = TravelpayoutsClient(settings.travelpayouts_token)
    notifier = TelegramNotifier(settings.telegram_bot_token, settings.telegram_chat_id)
    seen = load_seen()

    found_deals = []

    for destination in settings.destinations:
        for month in months_between(settings.date_start, settings.date_end):
            try:
                outbound_entries = client.month_matrix(
                    origin=settings.origin, destination=destination.code,
                    month=month, currency=settings.currency,
                )
            except Exception as exc:
                print(f"Erro consultando {settings.origin}->{destination.code} em {month}: {exc}")
                continue

            outbound = cheapest_in_range(outbound_entries, settings.date_start, settings.date_end)
            if outbound is None:
                continue

            if settings.one_way:
                total = outbound["value"]
                inbound = None
            else:
                try:
                    inbound_entries = client.month_matrix(
                        origin=destination.code, destination=settings.origin,
                        month=month, currency=settings.currency,
                    )
                except Exception as exc:
                    print(f"Erro consultando {destination.code}->{settings.origin} em {month}: {exc}")
                    continue

                inbound = cheapest_in_range(inbound_entries, settings.date_start, settings.date_end)
                if inbound is None:
                    continue
                total = outbound["value"] + inbound["value"]

            if total > destination.price_threshold_brl:
                continue

            key = deal_key(
                destination.code, outbound["depart_date"],
                inbound["depart_date"] if inbound else None, total,
            )
            if key in seen:
                continue

            seen.add(key)
            found_deals.append({
                "destination": destination,
                "outbound": outbound,
                "inbound": inbound,
                "total": total,
            })

    if found_deals:
        for deal in found_deals:
            dest = deal["destination"]
            outbound = deal["outbound"]
            msg_lines = [
                f"✈️ *Oferta encontrada: {settings.origin} → {dest.name} ({dest.code})*",
                f"Ida: {outbound['depart_date']} — {outbound['value']} {settings.currency.upper()}",
            ]
            if deal["inbound"]:
                inbound = deal["inbound"]
                msg_lines.append(
                    f"Volta: {inbound['depart_date']} — {inbound['value']} {settings.currency.upper()}"
                )
                msg_lines.append(
                    f"Total estimado (ida + volta somadas): {deal['total']} {settings.currency.upper()}"
                )
            else:
                msg_lines.append(f"Total: {deal['total']} {settings.currency.upper()}")
            msg_lines.append("_(preços de trechos avulsos somados — confirme o valor real ao comprar)_")
            notifier.send("\n".join(msg_lines))
        save_seen(seen)
        print(f"{len(found_deals)} oferta(s) nova(s) encontrada(s) e notificada(s).")
    else:
        print("Nenhuma oferta nova dentro do critério desta vez.")


if __name__ == "__main__":
    run()
