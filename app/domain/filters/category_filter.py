"""Фильтр по категории источника. Article не хранит категорию напрямую —
только source_url, поэтому фильтр принимает набор URL источников нужной
категории (их даёт Source Repository) и сверяет статьи по нему."""

from typing import Iterable, List

from app.domain.filters.base import Filter
from app.domain.models import Article


class CategoryFilter(Filter):
    def __init__(self, source_urls: Iterable[str]):
        self.source_urls = set(source_urls)

    def apply(self, articles: List[Article]) -> List[Article]:
        if not self.source_urls:
            return articles
        return [a for a in articles if a.source_url in self.source_urls]
