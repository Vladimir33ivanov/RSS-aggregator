"""PostgreSQL-реализация кэша статей за текущий день.

Интерфейс (load/save/is_today) совпадает с FileArticleCache, поэтому
FeedService не знает, откуда на самом деле берётся кэш (см.
app/dependencies.py — переключение по SOURCE_BACKEND).

Семантика повторяет файловую версию: хранится один "активный" день —
save() удаляет все строки с другой датой и перезаписывает список статей
за переданную дату. Это проще, чем накапливать историю, и достаточно для
того, как кэш используется сейчас (сброс раз в сутки)."""

from datetime import date as date_cls
from typing import List

from app.domain.models import Article
from app.infrastructure.cache import is_today as _is_today
from app.infrastructure.db import get_connection


class PostgresArticleCache:
    def __init__(self):
        self._conn = get_connection()
        self._conn.autocommit = True

    def load(self) -> dict:
        with self._conn.cursor() as cur:
            cur.execute("SELECT DISTINCT cached_date FROM articles ORDER BY cached_date DESC LIMIT 1")
            row = cur.fetchone()
            if row is None:
                return {"date": None, "items": []}
            cached_date = row[0]

            cur.execute(
                "SELECT title, link, pub_date, source_url FROM articles WHERE cached_date = %s",
                (cached_date,),
            )
            rows = cur.fetchall()

        items = [Article(title=r[0], link=r[1], pub_date=r[2], source_url=r[3]) for r in rows]
        return {"date": cached_date.strftime("%Y-%m-%d"), "items": items}

    def save(self, date: str, articles: List[Article]) -> None:
        parsed_date = date_cls.fromisoformat(date)
        with self._conn.cursor() as cur:
            # Кэш держит только один активный день — старые строки больше не нужны.
            cur.execute("DELETE FROM articles WHERE cached_date != %s", (parsed_date,))
            cur.execute("DELETE FROM articles WHERE cached_date = %s", (parsed_date,))
            cur.executemany(
                "INSERT INTO articles (title, link, pub_date, source_url, cached_date) "
                "VALUES (%s, %s, %s, %s, %s)",
                [(a.title, a.link, a.pub_date, a.source_url, parsed_date) for a in articles],
            )

    def is_today(self, date_str) -> bool:
        return _is_today(date_str)
