"""Подключение к PostgreSQL.

Параметры берутся из переменных окружения со значениями по умолчанию,
совпадающими с docker-compose.yml — поэтому локальный запуск через
`docker compose up -d` работает вообще без дополнительной настройки.
"""

import os

import psycopg2
from psycopg2.extensions import connection as PGConnection


def get_connection() -> PGConnection:
    return psycopg2.connect(
        host=os.getenv("DB_HOST", "localhost"),
        port=os.getenv("DB_PORT", "5432"),
        dbname=os.getenv("DB_NAME", "rss_aggregator"),
        user=os.getenv("DB_USER", "rss_user"),
        password=os.getenv("DB_PASSWORD", "rss_password"),
    )
