"""Интеграционные тесты PostgresSourceRepository — нужна настоящая БД.

Пропускаются автоматически, если не задана DATABASE_URL (см.
app/infrastructure/db.py) — то есть по умолчанию на локальной машине без
поднятого Postgres они просто не запустятся и не сломают остальной набор.

Локально: docker compose up -d, затем
  $env:DATABASE_URL="postgresql://rss_user:rss_password@localhost:5432/rss_aggregator"
  pytest -v tests/test_postgres_source_repository.py

В CI (.github/workflows/tests.yml) Postgres поднимается как service и
DATABASE_URL прокидывается автоматически."""

import os

import pytest

from app.infrastructure.postgres_source_repository import PostgresSourceRepository
from app.infrastructure.source_repository import DuplicateSourceError

pytestmark = pytest.mark.skipif(
    not os.getenv("DATABASE_URL"),
    reason="Требуется DATABASE_URL с доступной PostgreSQL (см. db/schema.sql)",
)


@pytest.fixture
def repo():
    repository = PostgresSourceRepository()
    yield repository
    # Уборка за тестом: удаляем всё, что сами же добавили (по префиксу
    # URL), чтобы прогоны не накапливали мусор в общей тестовой БД.
    with repository._conn:
        with repository._conn.cursor() as cur:
            cur.execute("DELETE FROM sources WHERE url LIKE 'https://pg-test%'")


def test_add_and_list(repo):
    added = repo.add("https://pg-test.example/rss", name="PG Test", category="tech")

    assert added.id is not None
    urls = {s.url for s in repo.list_all()}
    assert "https://pg-test.example/rss" in urls


def test_list_by_category(repo):
    repo.add("https://pg-test-tech.example/rss", name="Tech", category="tech")
    repo.add("https://pg-test-sport.example/rss", name="Sport", category="sport")

    tech_sources = repo.list_by_category("tech")

    assert any(s.url == "https://pg-test-tech.example/rss" for s in tech_sources)
    assert all(s.category == "tech" for s in tech_sources)


def test_duplicate_url_raises(repo):
    repo.add("https://pg-test-dup.example/rss", name="Dup")

    with pytest.raises(DuplicateSourceError):
        repo.add("https://pg-test-dup.example/rss", name="Dup again")


def test_delete(repo):
    added = repo.add("https://pg-test-delete.example/rss", name="Delete me")

    assert repo.delete(added.id) is True
    assert repo.delete(added.id) is False
