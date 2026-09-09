"""Carrega configuração (critérios de busca) e segredos (.env)."""

import os
from dataclasses import dataclass
from pathlib import Path

import yaml
from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parent.parent


@dataclass
class DateWindow:
    depart: str
    ret: str


@dataclass
class Settings:
    origin: str
    destination: str
    destination_name: str
    currency: str
    date_windows: list[DateWindow]
    price_threshold: float
    check_frequency_hours: int
    serpapi_key: str
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

    serpapi_key = os.environ.get("SERPAPI_KEY")
    telegram_bot_token = os.environ.get("TELEGRAM_BOT_TOKEN")
    telegram_chat_id = os.environ.get("TELEGRAM_CHAT_ID")

    missing = [name for name, val in [
        ("SERPAPI_KEY", serpapi_key),
        ("TELEGRAM_BOT_TOKEN", telegram_bot_token),
        ("TELEGRAM_CHAT_ID", telegram_chat_id),
    ] if not val]
    if missing:
        raise EnvironmentError(
            f"Faltando variáveis de ambiente: {', '.join(missing)}. Preencha o arquivo .env "
            "(veja .env.example)."
        )

    destination = raw["destination"]
    date_windows = [
        DateWindow(depart=str(w["depart"]), ret=str(w["return"]))
        for w in raw["date_windows"]
    ]

    return Settings(
        origin=raw["origin"],
        destination=destination["code"],
        destination_name=destination["name"],
        currency=raw.get("currency", "brl"),
        date_windows=date_windows,
        price_threshold=float(raw["price_threshold_brl"]),
        check_frequency_hours=int(raw.get("check_frequency_hours", 168)),
        serpapi_key=serpapi_key,
        telegram_bot_token=telegram_bot_token,
        telegram_chat_id=telegram_chat_id,
    )
