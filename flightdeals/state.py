"""Guarda quais ofertas já foram notificadas, para não repetir alerta a cada checagem."""

import json
from pathlib import Path

STATE_FILE = Path(__file__).resolve().parent.parent / "seen_deals.json"


def load_seen() -> set[str]:
    if not STATE_FILE.exists():
        return set()
    return set(json.loads(STATE_FILE.read_text(encoding="utf-8")))


def save_seen(seen: set[str]) -> None:
    STATE_FILE.write_text(json.dumps(sorted(seen)), encoding="utf-8")


def deal_key(destination_code: str, depart_date: str, return_date: str | None, price: float) -> str:
    return f"{destination_code}|{depart_date}|{return_date}|{price}"
