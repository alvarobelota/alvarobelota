"""Cliente para a Google Flights API da SerpApi (busca real, com conexões computadas)."""

import requests

BASE_URL = "https://serpapi.com/search"


class SerpApiClient:
    def __init__(self, api_key: str):
        self.api_key = api_key

    def search_round_trip(self, departure_id: str, arrival_id: str, outbound_date: str,
                           return_date: str, currency: str) -> list[dict]:
        """Busca voos de ida e volta reais (com conexões) pra uma data específica.

        Retorna a lista combinada de itinerários (best_flights + other_flights),
        cada um com pelo menos os campos 'price' e 'flights' (pernas do voo).
        """
        params = {
            "engine": "google_flights",
            "departure_id": departure_id,
            "arrival_id": arrival_id,
            "outbound_date": outbound_date,
            "return_date": return_date,
            "type": 1,  # ida e volta
            "currency": currency,
            "hl": "pt-br",
            "api_key": self.api_key,
        }
        resp = requests.get(BASE_URL, params=params, timeout=30)
        resp.raise_for_status()
        payload = resp.json()
        if payload.get("error"):
            raise RuntimeError(f"SerpApi retornou erro: {payload['error']}")
        return payload.get("best_flights", []) + payload.get("other_flights", [])
