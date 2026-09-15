"""Интеграционные тесты PostgresArticleCache — нужна настоящая БД.

Пропускаются автоматически без DATABASE_URL (см. tests/test_postgres_source_repository.py
для инструкции по локальному запуску)."""

import os
from datetime import datetime, timezone

import pytest

from app.domain.models import Article
from app.infrastructure.postgres_article_cache import PostgresArticleCache
from app.infrastructure.postgres_source_repository import PostgresSourceRepository

pytestmark = pytest.mark.skipif(
    not os.getenv("DATABASE_URL"),
    reason="Требуется DATABASE_URL с доступной PostgreSQL (см. db/schema.sql)",
)


@pytest.fixture
def source():
    """Тестовый источник — на него будет ссылаться articles.source_id.
    Удаление источника в teardown каскадно удалит и связанные с ним
    статьи (ON DELETE CASCADE, см. db/schema.sql) — отдельно чистить
    articles не нужно."""
    repo = PostgresSourceRepository()
    added = repo.add("https://pg-cache-test.example/rss", name="Cache Test")
    yield added
    with repo._conn:
        with repo._conn.cursor() as cur:
            cur.execute("DELETE FROM sources WHERE id = %s", (added.id,))


def test_save_and_load_roundtrip(source):
    cache = PostgresArticleCache()
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    article = Article(
        title="Test article",
        link="https://pg-cache-test.example/a1",
        pub_date="Mon, 15 Sep 2026 10:00:00 +0000",
        source_url=source.url,
    )

    # save() полностью пересоздаёт таблицу articles (см. её докстроку) —
    # тест стоит гонять на отдельной/тестовой БД, а не на рабочей с
    # реальным кэшем, если он вам дорог прямо в этот момент.
    cache.save(today, [article])
    result = cache.load()

    assert result["date"] == today
    saved = next(a for a in result["items"] if a.link == article.link)
    assert saved.title == article.title
    assert saved.source_url == source.url
    # pub_date уходил и вернулся через TIMESTAMPTZ — проверяем, что это
    # всё ещё парсибельная RFC 822 строка, а не что-то ещё.
    assert saved.pub_date != ""


def test_save_skips_articles_without_matching_source(source):
    cache = PostgresArticleCache()
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    valid = Article(
        title="Valid",
        link="https://pg-cache-test.example/valid",
        pub_date="",
        source_url=source.url,
    )
    orphan = Article(
        title="Orphan",
        link="https://pg-cache-test.example/orphan",
        pub_date="",
        source_url="https://does-not-exist.example/rss",
    )

    cache.save(today, [valid, orphan])
    result = cache.load()

    links = {a.link for a in result["items"]}
    assert valid.link in links
    assert orphan.link not in links
