"""Регрессионный тест: в исходном filter_by_days из filters.py `return result`
был внутри цикла, из-за чего обрабатывался только первый элемент списка.
Этот тест падал бы на старой версии логики."""

from datetime import datetime, timedelta, timezone

from app.domain.filters.date_range_filter import DateRangeFilter
from app.domain.models import Article


def _rfc822(dt: datetime) -> str:
    return dt.strftime("%a, %d %b %Y %H:%M:%S +0000")


def test_date_range_filter_checks_every_article():
    now = datetime.now(timezone.utc)
    articles = [
        Article(title="Recent 1", link="1", pub_date=_rfc822(now), source_url=""),
        Article(title="Recent 2", link="2", pub_date=_rfc822(now - timedelta(hours=1)), source_url=""),
        Article(title="Old", link="3", pub_date=_rfc822(now - timedelta(days=10)), source_url=""),
    ]

    result = DateRangeFilter(days=1).apply(articles)

    assert {a.link for a in result} == {"1", "2"}
