"""Перенесено из exporter.py (save_to_csv). Названия колонок (pubDate, а не
pub_date) сохранены для совместимости с уже закоммиченным news.csv."""

import csv
from typing import List

from app.domain.models import Article


def save_to_csv(articles: List[Article], filename: str = "news.csv") -> None:
    if not articles:
        return
    with open(filename, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["title", "link", "pubDate"])
        writer.writeheader()
        for article in articles:
            writer.writerow(
                {"title": article.title, "link": article.link, "pubDate": article.pub_date}
            )
