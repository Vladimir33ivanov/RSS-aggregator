-- Миграция для БД, уже созданной по старой схеме (articles.source_url TEXT,
-- articles.pub_date TEXT). Для новой базы всё это уже включено в
-- db/schema.sql — эта миграция не нужна.
--
-- Применение:
--   Get-Content db/migrations/001_articles_fk_and_timestamptz.sql | docker exec -i rss-aggregator-db psql -U rss_user -d rss_aggregator
--
-- sources НЕ трогаем и не теряем — миграция затрагивает только articles.
-- articles — это кэш на один активный день (перезаписывается каждый
-- запрос ленты), поэтому проще один раз его очистить, чем аккуратно
-- конвертировать временный текстовый формат pub_date построчно в SQL.

BEGIN;

TRUNCATE TABLE articles;

ALTER TABLE articles DROP COLUMN source_url;
ALTER TABLE articles ADD COLUMN source_id INTEGER NOT NULL REFERENCES sources(id) ON DELETE CASCADE;
ALTER TABLE articles ALTER COLUMN pub_date TYPE TIMESTAMPTZ USING NULL;

CREATE INDEX IF NOT EXISTS idx_articles_source_id ON articles (source_id);

COMMIT;
