"""Перенесено из sorter.py (sort_news)."""

from typing import List

from app.domain.models import Article


def sort_by_title(articles: List[Article], reverse: bool = False) -> List[Article]:
    return sorted(articles, key=lambda a: a.title, reverse=reverse)
