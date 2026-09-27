"""PostgreSQL-реализация репозитория источников.

Реализует тот же интерфейс (add/list_all/list_by_category/delete), что и
FileSourceRepository (см. docs/architecture-drivers.md — Repository
pattern). Благодаря этому замена бэкенда происходит только в
app/dependencies.py, без единой правки в FeedService или API-роутерах.

Уникальность url обеспечена ограничением UNIQUE на уровне таблицы
(db/schema.sql) — DuplicateSourceError поднимается при перехвате
psycopg2.errors.UniqueViolation, то есть проверка честно происходит в БД,
а не в Python, как это было в файловой версии.
"""

from typing import List

import psycopg2

from app.domain.models import Source
from app.infrastructure.db import get_connection
from app.infrastructure.source_repository import DuplicateSourceError


class PostgresSourceRepository:
    def __init__(self):
        self._conn = get_connection()
        self._conn.autocommit = True

    def add(self, url: str, name: str, category: str = "general") -> Source:
        try:
            with self._conn.cursor() as cur:
                cur.execute(
                    "INSERT INTO sources (url, name, category) VALUES (%s, %s, %s) RETURNING id",
                    (url, name, category),
                )
                new_id = cur.fetchone()[0]
        except psycopg2.errors.UniqueViolation:
            raise DuplicateSourceError(url)
        return Source(id=new_id, url=url, name=name, category=category)

    def list_all(self) -> List[Source]:
        with self._conn.cursor() as cur:
            cur.execute("SELECT id, url, name, category FROM sources ORDER BY id")
            rows = cur.fetchall()
        return [Source(id=r[0], url=r[1], name=r[2], category=r[3]) for r in rows]

    def list_by_category(self, category: str) -> List[Source]:
        with self._conn.cursor() as cur:
            cur.execute(
                "SELECT id, url, name, category FROM sources WHERE category = %s ORDER BY id",
                (category,),
            )
            rows = cur.fetchall()
        return [Source(id=r[0], url=r[1], name=r[2], category=r[3]) for r in rows]

    def delete(self, source_id: int) -> bool:
        with self._conn.cursor() as cur:
            cur.execute("DELETE FROM sources WHERE id = %s", (source_id,))
            return cur.rowcount > 0

    def get_stats(self) -> List[dict]:
        """Сколько статей сейчас в кэше у каждого источника — через
        хранимую функцию source_article_counts() (db/schema.sql), а не
        через агрегацию в Python. Специфично для Postgres-бэкенда: у
        FileSourceRepository такого метода нет — файловое хранилище не
        умеет считать на своей стороне, поэтому GET /sources/stats
        доступен только при SOURCE_BACKEND=postgres (см. sources.py)."""
        with self._conn.cursor() as cur:
            cur.execute("SELECT source_id, url, name, category, article_count FROM source_article_counts()")
            rows = cur.fetchall()
        return [
            {"id": r[0], "url": r[1], "name": r[2], "category": r[3], "article_count": r[4]}
            for r in rows
        ]
