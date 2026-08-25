"""Общие зависимости для FastAPI Depends() и для CLI (main.py). Здесь же —
единственная точка замены FileSourceRepository на SQLite-реализацию."""

from functools import lru_cache

from app.infrastructure.source_repository import FileSourceRepository
from app.services.feed_service import FeedService


@lru_cache
def get_source_repository() -> FileSourceRepository:
    return FileSourceRepository()


def get_feed_service() -> FeedService:
    return FeedService(get_source_repository())
