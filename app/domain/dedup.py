"""Перенесено из filters.py (deduplicate). Не оформлено как Filter-стратегия,
т.к. это не альтернативная тактика, а один обязательный шаг пайплайна."""

from typing import List

from app.domain.models import Article


def deduplicate(articles: List[Article]) -> List[Article]:
    seen = set()
    result = []
    for article in articles:
        key = article.link or article.title
        if key not in seen:
            seen.add(key)
            result.append(article)
    return result
