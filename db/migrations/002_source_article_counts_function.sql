-- Миграция для БД, созданной до появления хранимой функции. Для новой
-- базы это уже включено в db/schema.sql — эта миграция не нужна.
--
-- Применение:
--   Get-Content db/migrations/002_source_article_counts_function.sql | docker exec -i rss-aggregator-db psql -U rss_user -d rss_aggregator
--
-- CREATE OR REPLACE — безопасно выполнять повторно, ничьих данных не трогает.

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
