-- Демонстрация EXPLAIN ANALYZE на объёме данных, где разница между
-- Seq Scan и Index Scan реально видна.
--
-- Работает во временной таблице (CREATE TEMP TABLE) — не трогает реальные
-- sources/articles, автоматически удаляется в конце сессии psql.
--
-- Запуск:
--   docker exec -i rss-aggregator-db psql -U rss_user -d rss_aggregator < db/explain_demo.sql
-- (в PowerShell: Get-Content db/explain_demo.sql | docker exec -i rss-aggregator-db psql -U rss_user -d rss_aggregator)

CREATE TEMP TABLE sources_demo (
    id SERIAL PRIMARY KEY,
    url TEXT,
    category TEXT
);

-- 500 000 строк, категория — одна из 5 (примерное распределение как в sources)
INSERT INTO sources_demo (url, category)
SELECT
    'https://example.com/feed/' || i,
    (ARRAY['tech', 'sport', 'science', 'general', 'news'])[1 + floor(random() * 5)::int]
FROM generate_series(1, 500000) AS i;

\echo '--- Без индекса (ожидаем Seq Scan) ---'
EXPLAIN ANALYZE SELECT * FROM sources_demo WHERE category = 'tech';

CREATE INDEX idx_sources_demo_category ON sources_demo (category);
ANALYZE sources_demo;

\echo '--- С индексом (ожидаем Index Scan / Bitmap Index Scan) ---'
EXPLAIN ANALYZE SELECT * FROM sources_demo WHERE category = 'tech';

-- На таком объёме и с 5 равномерными категориями (~100k строк на
-- категорию, то есть 1/5 таблицы) планировщик Postgres МОЖЕТ всё равно
-- выбрать Seq Scan — потому что таблица маленькая по строке и найти 20%
-- строк проще целиком прочитать, чем прыгать по индексу. Это не ошибка.
-- Если хочешь увидеть Index Scan наглядно — отфильтруй по гораздо более
-- редкому значению, например по конкретному url:

\echo '--- Точечный запрос по PRIMARY KEY (всегда Index Scan) ---'
EXPLAIN ANALYZE SELECT * FROM sources_demo WHERE id = 250000;

\echo '--- Точечный запрос по индексированному url, если он уникален ---'
CREATE INDEX idx_sources_demo_url ON sources_demo (url);
EXPLAIN ANALYZE SELECT * FROM sources_demo WHERE url = 'https://example.com/feed/250000';
