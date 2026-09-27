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
-- вся таблица очищается при следующем save().
--
-- source_id — foreign key на sources, а не текстовый url: так Postgres
-- сам следит за целостностью (нельзя сослаться на несуществующий
-- источник), а удаление источника каскадно чистит его статьи из кэша.
--
-- pub_date — TIMESTAMPTZ, а не текст: дата парсится из RFC 822 (формат
-- RSS pubDate) на стороне приложения при записи в кэш (см.
-- PostgresArticleCache), что даёт возможность фильтровать/сортировать по
-- дате прямо в SQL, а не только в Python.
CREATE TABLE IF NOT EXISTS articles (
    id SERIAL PRIMARY KEY,
    title TEXT NOT NULL,
    link TEXT NOT NULL,
    pub_date TIMESTAMPTZ,
    source_id INTEGER NOT NULL REFERENCES sources(id) ON DELETE CASCADE,
    cached_date DATE NOT NULL
);

-- Индекс под load() (выборка последнего активного дня и его статей)
CREATE INDEX IF NOT EXISTS idx_articles_cached_date ON articles (cached_date);

-- Индекс под JOIN с sources в load() и под ON DELETE CASCADE
CREATE INDEX IF NOT EXISTS idx_articles_source_id ON articles (source_id);

-- Хранимая функция: сколько статей в текущем кэше у каждого источника.
-- LEFT JOIN — источники без статей в кэше тоже попадают в выборку,
-- с article_count = 0, а не пропадают из результата.
-- Используется PostgresSourceRepository.get_stats() (см. GET /sources/stats).
CREATE OR REPLACE FUNCTION source_article_counts()
RETURNS TABLE (
    source_id INTEGER,
    url TEXT,
    name TEXT,
    category TEXT,
    article_count BIGINT
)
LANGUAGE sql
STABLE
AS $$
    SELECT
        sources.id,
        sources.url,
        sources.name,
        sources.category,
        COUNT(articles.id) AS article_count
    FROM sources
    LEFT JOIN articles ON articles.source_id = sources.id
    GROUP BY sources.id, sources.url, sources.name, sources.category
    ORDER BY article_count DESC, sources.id;
$$;
