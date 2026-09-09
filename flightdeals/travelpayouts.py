"""Cliente para a Data API da Travelpayouts (preços mais baratos encontrados por rota)."""

from datetime import date
import requests

BASE_URL = "https://api.travelpayouts.com"


class TravelpayoutsClient:
    def __init__(self, token: str):
        self.token = token

    def month_matrix(self, origin: str, destination: str, month: date, currency: str,
                      one_way: bool = False) -> list[dict]:
        """Retorna o preço mais barato encontrado para cada dia de partida no mês informado."""
        params = {
            "currency": currency,
            "origin": origin,
            "destination": destination,
            "month": month.strftime("%Y-%m-01"),
            "show_to_affiliates": "true",
            "one_way": "true" if one_way else "false",
        }
        headers = {"X-Access-Token": self.token}
        resp = requests.get(f"{BASE_URL}/v1/prices/month-matrix", params=params,
                             headers=headers, timeout=20)
        resp.raise_for_status()
        payload = resp.json()
        if not payload.get("success", True):
            raise RuntimeError(f"Travelpayouts API retornou erro: {payload}")
        return payload.get("data", [])
