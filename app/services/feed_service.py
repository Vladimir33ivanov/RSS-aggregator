"""Application service: оркестрирует получение фидов, кэш, фильтрацию,
дедупликацию и сортировку. Логика перенесена из main.py (merge_with_cache
и основной пайплайн). Используется и CLI, и API — не дублируется."""

from datetime import datetime
from typing import List, Optional

from app.domain.dedup import deduplicate
from app.domain.filters.category_filter import CategoryFilter
from app.domain.filters.date_range_filter import DateRangeFilter
from app.domain.filters.keyword_filter import KeywordFilter
from app.domain.models import Article
from app.domain.sorting import sort_by_title
from app.infrastructure import cache as cache_infra
from app.infrastructure.rss_fetcher import fetch_source
from app.infrastructure.source_repository import FileSourceRepository


class FeedService:
    def __init__(self, source_repository: FileSourceRepository):
        self._sources = source_repository

    def get_feed(
        self,
        keyword: Optional[str] = None,
        days: Optional[int] = None,
        category: Optional[str] = None,
        sort_reverse: Optional[bool] = None,
        use_cache: bool = True,
        only_new: bool = False,
    ) -> List[Article]:
        articles: List[Article] = []
        for source in self._sources.list_all():
            articles.extend(fetch_source(source.url))

        if use_cache:
            articles = self._merge_with_cache(articles, only_new=only_new)

        if category:
            category_urls = [s.url for s in self._sources.list_by_category(category)]
            articles = CategoryFilter(category_urls).apply(articles)
        if keyword:
            articles = KeywordFilter(keyword).apply(articles)
        if days:
            articles = DateRangeFilter(days).apply(articles)

        articles = deduplicate(articles)

        if sort_reverse is not None:
            articles = sort_by_title(articles, reverse=sort_reverse)

        return articles

    def _merge_with_cache(self, new_articles: List[Article], only_new: bool) -> List[Article]:
        cache = cache_infra.load_cache()
        today_str = datetime.now().strftime("%Y-%m-%d")

        if cache_infra.is_today(cache["date"]):
            existing_titles = {a.title for a in cache["items"]}
            unique_new = [a for a in new_articles if a.title not in existing_titles]
            merged = cache["items"] + unique_new
            cache_infra.save_cache(today_str, merged)
            return unique_new if only_new else merged

        cache_infra.save_cache(today_str, new_articles)
        return new_articles
