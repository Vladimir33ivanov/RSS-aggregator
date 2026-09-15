# Changelog

Формат основан на [Keep a Changelog](https://keepachangelog.com/ru/1.0.0/),
версии — по [Semantic Versioning](https://semver.org/lang/ru/).

## [Unreleased]

### Added
- Фильтрация ленты и списка источников по категории:
  `GET /feed?category=...`, `GET /sources?category=...`, `--category` в CLI
- Тесты для `FileSourceRepository` (загрузка, добавление, удаление,
  фильтрация по категории, защита от дублей)
- `DELETE /sources/{id}` — удаление источника
- Защита от дублирующихся источников (`DuplicateSourceError`, 409 в API)
- CI на GitHub Actions: автозапуск pytest при push/PR в `main`
- `.gitattributes` для нормализации переносов строк (LF)
- PostgreSQL как альтернативный бэкенд хранилища источников и кэша статей:
  `docker-compose.yml`, `db/schema.sql`, `PostgresSourceRepository`,
  `PostgresArticleCache`, переключение через переменную окружения
  `SOURCE_BACKEND=postgres`
- `articles.source_id` — foreign key на `sources.id` (`ON DELETE CASCADE`)
  вместо текстового `source_url`; `pub_date` — `TIMESTAMPTZ` вместо текста
  (конвертация RFC 822 <-> datetime в `PostgresArticleCache`)
- `db/migrations/001_articles_fk_and_timestamptz.sql` — миграция для БД,
  созданных по старой схеме
- `db/explain_demo.sql` — демонстрация `EXPLAIN ANALYZE` (Seq Scan vs
  Index Scan) на 500 000 сгенерированных строк, без затрагивания реальных
  данных
- `scripts/backup_postgres.sh` — `pg_dump` с ротацией старых бэкапов и
  логированием, для запуска через cron в WSL
- Интеграционные тесты `tests/test_postgres_source_repository.py` и
  `tests/test_postgres_article_cache.py` (пропускаются без `DATABASE_URL`)
- Postgres как service в CI (`.github/workflows/tests.yml`) — Postgres-тесты
  теперь реально гоняются на каждый push, а не только локально

### Fixed
- `PostgresArticleCache.save()`: DELETE + серия INSERT теперь в одной
  транзакции (`with self._conn:` вместо `autocommit=True`) — раньше
  падение на середине записи могло оставить кэш пустым
- Упрощён `save()`: два DELETE подряд (`!= date` и `= date`), вместе
  покрывавшие всю таблицу, заменены на один безусловный `DELETE FROM articles`

### Planned
- Управление источниками и категориями через веб-интерфейс
- Умная фильтрация/рекомендации

## [2.0.0-alpha.1] - 2026-08-25

### Added
- Веб-API на FastAPI: `GET /health`, `GET/POST /sources`, `GET /feed`
- Слоистая архитектура: `app/domain`, `app/infrastructure`, `app/services`, `app/api`
- Тесты (pytest) на фильтры, дедупликацию и API

### Changed
- Логика из `filters.py`, `cache_manager.py`, `exporter.py`, `formatter.py`,
  `sorter.py`, `storage.py` перенесена в `app/`; `main.py` стал тонкой
  CLI-обёрткой над общей логикой с веб-API
- `KeywordFilter` поддерживает несколько ключевых слов через запятую

### Fixed
- Исправлена ошибка в фильтре по дате (`filter_by_days`): раньше
  обрабатывался только первый элемент списка из-за неверного отступа `return`

### Removed
- Флаги CLI `--url` и `--limit` (разовый источник без сохранения) — источники
  теперь берутся только из репозитория (`sources.txt`)

## [1.0.0] - CLI-версия

Первая рабочая версия — консольный RSS-агрегатор.

### Added
- Получение и разбор RSS-фидов из списка источников (`sources.txt`)
- Фильтрация по ключевым словам и по давности публикации
- Дедупликация новостей
- Кэш за текущий день
- Экспорт в JSON и CSV, вывод таблицей в консоль
