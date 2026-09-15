"""Файловая реализация кэша статей — тонкая обёртка над функциями из
cache.py в виде класса с тем же интерфейсом (load/save/is_today), что и
PostgresArticleCache (см. postgres_article_cache.py). Это тот же приём
Repository pattern, что и для источников (см. source_repository.py) —
FeedService зависит от интерфейса, а не от конкретного хранилища."""

from typing import List

from app.domain.models import Article
from app.infrastructure import cache as _cache


class FileArticleCache:
    def __init__(self, path: str = _cache.DEFAULT_CACHE_FILE):
        self._path = path

    def load(self) -> dict:
        return _cache.load_cache(self._path)

    def save(self, date: str, articles: List[Article]) -> None:
        _cache.save_cache(date, articles, self._path)

    def is_today(self, date_str) -> bool:
        return _cache.is_today(date_str)
