"""Cliente para a Data API da Travelpayouts (preços mais baratos encontrados por rota).

A API só guarda preços de trechos individuais (passagens de ida avulsas
encontradas em buscas de outros usuários) — não existe cache de passagem
de ida-e-volta emitida junto. Por isso o app busca cada perna separadamente
e soma as duas pra estimar o total de uma viagem de ida e volta.
"""

from datetime import date
import requests

BASE_URL = "https://api.travelpayouts.com"


class TravelpayoutsClient:
    def __init__(self, token: str):
        self.token = token

    def month_matrix(self, origin: str, destination: str, month: date, currency: str) -> list[dict]:
        """Retorna o preço mais barato encontrado para cada dia de partida no mês informado,
        para o trecho origin -> destination (só ida)."""
        params = {
            "currency": currency,
            "origin": origin,
            "destination": destination,
            "depart_date": month.strftime("%Y-%m"),
            "show_to_affiliates": "true",
        }
        headers = {"X-Access-Token": self.token}
        resp = requests.get(f"{BASE_URL}/v2/prices/month-matrix", params=params,
                             headers=headers, timeout=20)
        resp.raise_for_status()
        payload = resp.json()
        if not payload.get("success", True):
            raise RuntimeError(f"Travelpayouts API retornou erro: {payload}")
        return payload.get("data", [])
