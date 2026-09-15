"""PostgreSQL-реализация кэша статей за текущий день.

Интерфейс (load/save/is_today) совпадает с FileArticleCache, поэтому
FeedService не знает, откуда на самом деле берётся кэш (см.
app/dependencies.py — переключение по SOURCE_BACKEND).

Семантика повторяет файловую версию: хранится один "активный" день —
save() полностью пересоздаёт список статей за переданную дату.

Хранение связано с sources через foreign key (articles.source_id ->
sources.id, ON DELETE CASCADE, см. db/schema.sql) — если источник удалён,
его статьи в кэше удаляются автоматически, а не остаются "осиротевшими"
записями с текстовым url в никуда.

pub_date хранится в БД как TIMESTAMPTZ, а не текст. Конвертация в обе
стороны (RFC 822 строка <-> datetime) происходит здесь же, в
infrastructure-слое, через email.utils (тот же парсер, что уже
использует DateRangeFilter) — домену и остальному коду всё равно не
важно, что это Postgres: Article.pub_date всегда остаётся строкой,
независимо от активного бэкенда.

Обе операции обёрнуты в `with self._conn:` (транзакция), а не в
autocommit — save() делает DELETE + пачку INSERT, и они должны либо
применяться вместе, либо не применяться вовсе, если что-то упадёт
посередине."""

from datetime import date as date_cls
from email.utils import format_datetime, parsedate_to_datetime
from typing import List

from app.domain.models import Article
from app.infrastructure.cache import is_today as _is_today
from app.infrastructure.db import get_connection


def _parse_pub_date(pub_date: str):
    """RFC 822 строка (как её отдаёт RSS pubDate) -> datetime | None.
    Если дата отсутствует или не парсится — None (NULL в БД), точно так
    же, как файловый кэш просто хранил пустую строку."""
    if not pub_date:
        return None
    try:
        return parsedate_to_datetime(pub_date)
    except (TypeError, ValueError):
        return None


def _format_pub_date(dt) -> str:
    """Обратное преобразование: datetime из БД -> RFC 822 строка, чтобы
    Article.pub_date выглядел одинаково независимо от бэкенда."""
    if dt is None:
        return ""
    return format_datetime(dt)


class PostgresArticleCache:
    def __init__(self):
        self._conn = get_connection()

    def load(self) -> dict:
        with self._conn:
            with self._conn.cursor() as cur:
                cur.execute(
                    "SELECT DISTINCT cached_date FROM articles ORDER BY cached_date DESC LIMIT 1"
                )
                row = cur.fetchone()
                if row is None:
                    return {"date": None, "items": []}
                cached_date = row[0]

                cur.execute(
                    """
                    SELECT articles.title, articles.link, articles.pub_date, sources.url
                    FROM articles
                    JOIN sources ON sources.id = articles.source_id
                    WHERE articles.cached_date = %s
                    """,
                    (cached_date,),
                )
                rows = cur.fetchall()

        items = [
            Article(title=r[0], link=r[1], pub_date=_format_pub_date(r[2]), source_url=r[3])
            for r in rows
        ]
        return {"date": cached_date.strftime("%Y-%m-%d"), "items": items}

    def save(self, date: str, articles: List[Article]) -> None:
        parsed_date = date_cls.fromisoformat(date)
        with self._conn:
            with self._conn.cursor() as cur:
                # Кэш держит только один активный день — таблица полностью
                # очищается перед записью нового набора статей.
                cur.execute("DELETE FROM articles")
                cur.executemany(
                    """
                    INSERT INTO articles (title, link, pub_date, source_id, cached_date)
                    SELECT %s, %s, %s, sources.id, %s
                    FROM sources
                    WHERE sources.url = %s
                    """,
                    [
                        (
                            a.title,
                            a.link,
                            _parse_pub_date(a.pub_date),
                            parsed_date,
                            a.source_url,
                        )
                        for a in articles
                    ],
                )
                # Если source_url статьи не совпал ни с одним источником
                # (источник уже удалили) — INSERT ... SELECT просто ничего
                # не вставит для этой статьи, она тихо выпадает из кэша.

    def is_today(self, date_str) -> bool:
        return _is_today(date_str)
