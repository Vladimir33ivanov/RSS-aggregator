-- Схема таблицы источников для PostgreSQL.
-- Выполняется автоматически при первом старте контейнера
-- (см. docker-compose.yml, docker-entrypoint-initdb.d).

CREATE TABLE IF NOT EXISTS sources (
    id SERIAL PRIMARY KEY,
    url TEXT NOT NULL UNIQUE,
    name TEXT NOT NULL,
    category TEXT NOT NULL DEFAULT 'general'
);

-- Индекс под фильтрацию /sources?category= и /feed?category=
CREATE INDEX IF NOT EXISTS idx_sources_category ON sources (category);

-- Кэш статей за текущий день (замена news_cache.json, см.
-- PostgresArticleCache). Хранится всегда только один "активный" день —
-- старые строки удаляются при следующем save().
CREATE TABLE IF NOT EXISTS articles (
    id SERIAL PRIMARY KEY,
    title TEXT NOT NULL,
    link TEXT NOT NULL,
    pub_date TEXT,
    source_url TEXT NOT NULL,
    cached_date DATE NOT NULL
);

-- Индекс под load() (выборка последнего активного дня и его статей)
CREATE INDEX IF NOT EXISTS idx_articles_cached_date ON articles (cached_date);
