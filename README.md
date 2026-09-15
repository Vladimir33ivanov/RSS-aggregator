# RSS-агрегатор

Личный агрегатор новостей из RSS-источников. Работает в двух видах —
консольная утилита и веб-сервис на FastAPI — оба используют одну и ту же
логику (см. [`docs/architecture-drivers.md`](docs/architecture-drivers.md)).

## Возможности

- Получение новостей из списка RSS-источников
- Фильтрация по ключевым словам, давности публикации и категории источника
- Дедупликация и сортировка
- Кэш за текущий день, экспорт в JSON/CSV (CLI)
- Веб-API: добавление/удаление источников, лента с фильтрами, интерактивная документация
- Хранилище источников и кэш статей — файл или PostgreSQL, переключается
  одной переменной окружения (см. [Хранилище данных](#хранилище-данных))

## Быстрый старт

```bash
python -m venv .venv
.venv\Scripts\activate        # Windows; на Linux/macOS: source .venv/bin/activate
pip install -r requirements.txt
```

### Консольная версия

```bash
python main.py --keyword AI --category tech --days 7 --sort desc
```

Доступные флаги:

| Флаг | Значение |
|---|---|
| `--keyword` | фильтр по ключевым словам (через запятую) |
| `--category` | фильтр по категории источника |
| `--days` | новости за последние N дней |
| `--sort {asc,desc}` | сортировка по заголовку |
| `--format {json,csv,all}` | формат вывода (по умолчанию `all`) |
| `--new` | показать только новые новости за сегодня |

### Веб-версия

```bash
uvicorn app.main:app --reload
```

Открыть `http://127.0.0.1:8000/docs` — интерактивная документация (Swagger),
там же можно вызывать все эндпоинты без написания кода.

| Эндпоинт | Описание |
|---|---|
| `GET /health` | проверка, что сервис жив |
| `GET /sources` | список источников (`?category=...` — фильтр) |
| `POST /sources` | добавить источник |
| `DELETE /sources/{id}` | удалить источник |
| `GET /feed` | лента (`?keyword=`, `?days=`, `?category=`, `?sort=asc\|desc`) |

## Хранилище данных

По умолчанию источники хранятся в `sources.txt`, а кэш статей — в
`news_cache.json`. Это самый простой вариант, ничего дополнительно
устанавливать не нужно.

Есть и вариант с PostgreSQL — для этого в проекте уже готовы
`docker-compose.yml` и схема БД (`db/schema.sql`):

```bash
docker compose up -d              # поднимет Postgres, схема применится сама
```

Переключение бэкенда — одна переменная окружения:

```bash
# Windows PowerShell
$env:SOURCE_BACKEND="postgres"; uvicorn app.main:app --reload

# Linux/macOS
SOURCE_BACKEND=postgres uvicorn app.main:app --reload
```

Без установленной переменной (или `SOURCE_BACKEND=file`) всё работает как
раньше, через файлы. Подключение к БД настраивается через `DB_HOST`,
`DB_PORT`, `DB_NAME`, `DB_USER`, `DB_PASSWORD` (значения по умолчанию
совпадают с `docker-compose.yml`, см. `app/infrastructure/db.py`).

Оба бэкенда реализуют один и тот же интерфейс (Repository pattern, см.
[`docs/architecture-drivers.md`](docs/architecture-drivers.md)), поэтому
`FeedService` и API-роутеры не знают и не зависят от того, какое хранилище
используется на самом деле.

`articles.source_id` — foreign key на `sources.id` (`ON DELETE CASCADE`),
`pub_date` хранится как `TIMESTAMPTZ`. Если база уже была создана по
старой схеме (`source_url TEXT`, `pub_date TEXT`) — накатить
[`db/migrations/001_articles_fk_and_timestamptz.sql`](db/migrations/001_articles_fk_and_timestamptz.sql):

```powershell
Get-Content db/migrations/001_articles_fk_and_timestamptz.sql | docker exec -i rss-aggregator-db psql -U rss_user -d rss_aggregator
```

Миграция очищает таблицу `articles` (это одноразовый кэш на текущий день,
не жалко) — `sources` она не трогает.

### EXPLAIN ANALYZE на объёме данных

[`db/explain_demo.sql`](db/explain_demo.sql) — самодостаточный скрипт:
создаёт временную таблицу, наполняет её 500 000 строк через
`generate_series` и показывает план запроса до/после индекса:

```powershell
Get-Content db/explain_demo.sql | docker exec -i rss-aggregator-db psql -U rss_user -d rss_aggregator
```

Не трогает реальные `sources`/`articles`, временная таблица удаляется
сама в конце сессии psql.

## Резервное копирование

[`scripts/backup_postgres.sh`](scripts/backup_postgres.sh) — `pg_dump` из
контейнера в сжатый архив с датой в имени, автоматическое удаление
бэкапов старше 7 дней, логирование каждого шага в `logs/backup.log`.
Запускается из WSL:

```bash
chmod +x scripts/backup_postgres.sh   # один раз
./scripts/backup_postgres.sh
```

Для регулярного запуска — через `cron` (пример на каждый день в 3:00,
`crontab -e`):

```
0 3 * * * cd /путь/к/проекту && ./scripts/backup_postgres.sh
```

## Структура проекта

```
app/
├── api/            # FastAPI-роутеры (HTTP-слой)
├── services/       # оркестрация (Feed Service)
├── domain/         # бизнес-логика: модели, фильтры, сортировка, дедупликация
└── infrastructure/ # получение RSS, кэш и хранилище источников (файл или Postgres)
db/
├── schema.sql          # схема PostgreSQL (sources, articles) для новой БД
├── migrations/         # миграции для уже существующей БД
└── explain_demo.sql    # демо EXPLAIN ANALYZE на большом объёме данных
scripts/
└── backup_postgres.sh  # pg_dump + ротация + логирование, для cron/WSL
docker-compose.yml  # локальный Postgres для разработки
main.py             # тонкая CLI-обёртка над app/ (не дублирует логику)
tests/              # pytest (test_postgres_* — интеграционные, нужен DATABASE_URL)
```

## Документация

- [`docs/vision.md`](docs/vision.md) — видение продукта и дорожная карта
- [`docs/architecture-drivers.md`](docs/architecture-drivers.md) — архитектурные драйверы и первая ADD-итерация
- [`CHANGELOG.md`](CHANGELOG.md) — история версий

## Версионирование

Проект использует [Semantic Versioning](https://semver.org/lang/ru/):

- `v1.0.0` — исходная CLI-версия
- `v2.0.0-alpha.1` — текущая, слоистая архитектура + веб-API (в разработке)

## Тесты

```bash
pytest -v
```

Тесты на Postgres-бэкенд (`tests/test_postgres_*.py`) — интеграционные,
пропускаются автоматически без переменной `DATABASE_URL`. Чтобы прогнать
их локально (нужен поднятый `docker compose up -d`):

```powershell
$env:DATABASE_URL="postgresql://rss_user:rss_password@localhost:5432/rss_aggregator"
pytest -v
```

В CI (`.github/workflows/tests.yml`) Postgres поднимается как service
автоматически, `DATABASE_URL` прокидывается сам.
