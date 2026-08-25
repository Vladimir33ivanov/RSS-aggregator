"""Перенесено из filters.py (filter_by_days).

Исправлена ошибка исходной реализации: `return result` был внутри цикла
for, из-за чего обрабатывался только первый элемент списка. Здесь return
вынесен за пределы цикла — фильтр теперь корректно проверяет все статьи."""

from datetime import datetime, timedelta, timezone
from email.utils import parsedate_to_datetime
from typing import List

from app.domain.filters.base import Filter
from app.domain.models import Article


class DateRangeFilter(Filter):
    def __init__(self, days: int):
        self.days = days

    def apply(self, articles: List[Article]) -> List[Article]:
        if not self.days:
            return articles

        cutoff = datetime.now(timezone.utc) - timedelta(days=self.days)
        result = []
        for article in articles:
            if not article.pub_date:
                result.append(article)
                continue
            try:
                dt = parsedate_to_datetime(article.pub_date)
                if dt >= cutoff:
                    result.append(article)
            except Exception:
                result.append(article)
        return result
