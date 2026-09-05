# Changelog

Формат основан на [Keep a Changelog](https://keepachangelog.com/ru/1.0.0/),
версии — по [Semantic Versioning](https://semver.org/lang/ru/).

## [Unreleased]

### Added
- Фильтрация ленты и списка источников по категории:
  `GET /feed?category=...`, `GET /sources?category=...`, `--category` в CLI

### Planned
- Хранилище источников на SQLite вместо файла sources.txt
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
