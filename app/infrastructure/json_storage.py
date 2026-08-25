"""Перенесено из storage.py (save_to_json)."""

import json
from dataclasses import asdict
from datetime import datetime
from typing import List

from app.domain.models import Article


def save_to_json(articles: List[Article], filename: str = "news.json") -> None:
    output = {
        "timestamp": datetime.now().isoformat(),
        "count": len(articles),
        "items": [asdict(a) for a in articles],
    }
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=4)
