"""Carrega configuração (critérios de busca) e segredos (.env)."""

import os
from dataclasses import dataclass
from datetime import date
from pathlib import Path

import yaml
from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parent.parent


@dataclass
class Destination:
    code: str
    name: str
    price_threshold_brl: float


@dataclass
class Settings:
    origin: str
    currency: str
    destinations: list[Destination]
    date_start: date
    date_end: date
    one_way: bool
    check_frequency_hours: int
    travelpayouts_token: str
    telegram_bot_token: str
    telegram_chat_id: str


def load_settings(config_path: Path | None = None) -> Settings:
    load_dotenv(ROOT / ".env")

    config_path = config_path or (ROOT / "flightdeals" / "config.yaml")
    if not config_path.exists():
        raise FileNotFoundError(
            f"{config_path} não existe. Copie config.example.yaml para config.yaml "
            "e preencha com seus critérios de busca."
        )

    with open(config_path, encoding="utf-8") as f:
        raw = yaml.safe_load(f)

    travelpayouts_token = os.environ.get("TRAVELPAYOUTS_TOKEN")
    telegram_bot_token = os.environ.get("TELEGRAM_BOT_TOKEN")
    telegram_chat_id = os.environ.get("TELEGRAM_CHAT_ID")

    missing = [name for name, val in [
        ("TRAVELPAYOUTS_TOKEN", travelpayouts_token),
        ("TELEGRAM_BOT_TOKEN", telegram_bot_token),
        ("TELEGRAM_CHAT_ID", telegram_chat_id),
    ] if not val]
    if missing:
        raise EnvironmentError(
            f"Faltando variáveis de ambiente: {', '.join(missing)}. Preencha o arquivo .env "
            "(veja .env.example)."
        )

    return Settings(
        origin=raw["origin"],
        currency=raw.get("currency", "brl"),
        destinations=[Destination(**d) for d in raw["destinations"]],
        date_start=raw["date_range"]["start"],
        date_end=raw["date_range"]["end"],
        one_way=bool(raw.get("one_way", False)),
        check_frequency_hours=int(raw.get("check_frequency_hours", 24)),
        travelpayouts_token=travelpayouts_token,
        telegram_bot_token=telegram_bot_token,
        telegram_chat_id=telegram_chat_id,
    )
