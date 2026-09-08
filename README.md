# RSS-агрегатор

Личный агрегатор новостей из RSS-источников. Работает в двух видах —
консольная утилита и веб-сервис на FastAPI — оба используют одну и ту же
логику (см. [`docs/architecture-drivers.md`](docs/architecture-drivers.md)).

## Возможности

- Получение новостей из списка RSS-источников
- Фильтрация по ключевым словам, давности публикации и категории источника
- Дедупликация и сортировка
- Кэш за текущий день, экспорт в JSON/CSV (CLI)
- Веб-API: добавление источников, лента с фильтрами, интерактивная документация

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
| `GET /feed` | лента (`?keyword=`, `?days=`, `?category=`, `?sort=asc\|desc`) |

## Структура проекта

```
app/
├── api/            # FastAPI-роутеры (HTTP-слой)
├── services/       # оркестрация (Feed Service)
├── domain/         # бизнес-логика: модели, фильтры, сортировка, дедупликация
└── infrastructure/ # получение RSS, кэш, файлы, хранилище источников
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
