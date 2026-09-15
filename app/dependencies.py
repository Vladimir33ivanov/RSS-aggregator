import os
from functools import lru_cache

from app.infrastructure.source_repository import FileSourceRepository
from app.services.feed_service import FeedService


@lru_cache
def get_source_repository():
    """Выбор бэкенда хранилища источников через переменную окружения
    SOURCE_BACKEND. По умолчанию — файл (без изменений в поведении для
    тех, кто ничего не настраивал). SOURCE_BACKEND=postgres переключает
    на PostgreSQL (см. docker-compose.yml и db/schema.sql).

    Именно ради такой замены в одну строку и был введён Repository
    pattern — FeedService и API-роутеры работают с интерфейсом, а не с
    конкретной реализацией (см. docs/architecture-drivers.md)."""
    backend = os.getenv("SOURCE_BACKEND", "file")
    if backend == "postgres":
        from app.infrastructure.postgres_source_repository import PostgresSourceRepository

        return PostgresSourceRepository()
    return FileSourceRepository()


@lru_cache
def get_article_cache():
    """Аналогичное переключение для кэша статей (news_cache.json vs
    таблица articles в Postgres) — один и тот же SOURCE_BACKEND решает
    сразу за оба хранилища, чтобы не плодить отдельные флаги."""
    backend = os.getenv("SOURCE_BACKEND", "file")
    if backend == "postgres":
        from app.infrastructure.postgres_article_cache import PostgresArticleCache

        return PostgresArticleCache()
    from app.infrastructure.article_cache import FileArticleCache

    return FileArticleCache()


def get_feed_service() -> FeedService:
    return FeedService(get_source_repository(), get_article_cache())
