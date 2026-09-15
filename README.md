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

## Структура проекта

```
app/
├── api/            # FastAPI-роутеры (HTTP-слой)
├── services/       # оркестрация (Feed Service)
├── domain/         # бизнес-логика: модели, фильтры, сортировка, дедупликация
└── infrastructure/ # получение RSS, кэш и хранилище источников (файл или Postgres)
db/
└── schema.sql      # схема PostgreSQL (sources, articles)
docker-compose.yml  # локальный Postgres для разработки
main.py             # тонкая CLI-обёртка над app/ (не дублирует логику)
tests/              # pytest
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
