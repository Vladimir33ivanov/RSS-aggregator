"""Перенесено из cache_manager.py, адаптировано под Article вместо dict."""

import json
import os
from dataclasses import asdict
from datetime import datetime
from typing import List

from app.domain.models import Article

DEFAULT_CACHE_FILE = "news_cache.json"


def load_cache(path: str = DEFAULT_CACHE_FILE) -> dict:
    if os.path.exists(path):
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
            data["items"] = [Article(**item) for item in data["items"]]
            return data
        except (json.JSONDecodeError, TypeError, KeyError):
            # Кэш повреждён или в старом/несовместимом формате (например,
            # остался от версии до переноса логики в app/) — не роняем
            # приложение, а просто считаем, что валидного кэша на сегодня нет.
            pass
    return {"date": None, "items": []}


def save_cache(date: str, articles: List[Article], path: str = DEFAULT_CACHE_FILE) -> None:
    with open(path, "w", encoding="utf-8") as f:
        json.dump(
            {"date": date, "items": [asdict(a) for a in articles]},
            f,
            ensure_ascii=False,
            indent=4,
        )


def is_today(date_str) -> bool:
    return date_str == datetime.now().strftime("%Y-%m-%d")
