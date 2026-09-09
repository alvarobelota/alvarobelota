"""Busca periódica de passagens em oferta (ida e volta real) e alerta via Telegram.

Uso:
    python -m flightdeals.main
"""

from flightdeals.config import load_settings
from flightdeals.notifier import TelegramNotifier
from flightdeals.serpapi_client import SerpApiClient
from flightdeals.state import deal_key, load_seen, save_seen


def run() -> None:
    settings = load_settings()
    client = SerpApiClient(settings.serpapi_key)
    notifier = TelegramNotifier(settings.telegram_bot_token, settings.telegram_chat_id)
    seen = load_seen()

    found_deals = []

    for window in settings.date_windows:
        try:
            itineraries = client.search_round_trip(
                departure_id=settings.origin,
                arrival_id=settings.destination,
                outbound_date=window.depart,
                return_date=window.ret,
                currency=settings.currency,
            )
        except Exception as exc:
            print(f"Erro consultando {settings.origin}->{settings.destination} "
                  f"({window.depart} / {window.ret}): {exc}")
            continue

        if not itineraries:
            continue

        cheapest = min(itineraries, key=lambda it: it["price"])
        price = cheapest["price"]
        if price > settings.price_threshold:
            continue

        key = deal_key(settings.destination, window.depart, window.ret, price)
        if key in seen:
            continue

        seen.add(key)
        found_deals.append({"window": window, "price": price, "itinerary": cheapest})

    if found_deals:
        for deal in found_deals:
            window = deal["window"]
            msg_lines = [
                f"✈️ *Oferta encontrada: {settings.origin} → "
                f"{settings.destination_name} ({settings.destination})*",
                f"Ida: {window.depart}",
                f"Volta: {window.ret}",
                f"Preço (ida e volta): {deal['price']} {settings.currency.upper()}",
            ]
            legs = deal["itinerary"].get("flights", [])
            stops = max(len(legs) - 1, 0)
            if stops:
                msg_lines.append(f"Conexões na ida: {stops}")
            notifier.send("\n".join(msg_lines))
        save_seen(seen)
        print(f"{len(found_deals)} oferta(s) nova(s) encontrada(s) e notificada(s).")
    else:
        print("Nenhuma oferta nova dentro do critério desta vez.")


if __name__ == "__main__":
    run()
