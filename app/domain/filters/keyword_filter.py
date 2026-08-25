"""Перенесено из filters.py (filter_by_keyword) — поддерживает несколько
ключевых слов через запятую, статья проходит, если совпало любое из них."""

from typing import List

from app.domain.filters.base import Filter
from app.domain.models import Article


class KeywordFilter(Filter):
    def __init__(self, keyword: str):
        self.keywords = (
            [k.strip().lower() for k in keyword.split(",") if k.strip()]
            if keyword
            else []
        )

    def apply(self, articles: List[Article]) -> List[Article]:
        if not self.keywords:
            return articles
        return [
            a for a in articles
            if any(k in a.title.lower() for k in self.keywords)
        ]
