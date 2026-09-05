"""CLI-обёртка поверх app/. Вся логика (получение фидов, кэш, фильтрация,
дедупликация, сортировка) живёт в app/services/feed_service.py и
переиспользуется веб-API (app/api/routes/feed.py) — здесь только разбор
аргументов и вывод. См. docs/architecture-drivers.md."""

import argparse

from app.cli.formatter import print_as_table
from app.dependencies import get_feed_service, get_source_repository
from app.infrastructure.csv_exporter import save_to_csv
from app.infrastructure.json_storage import save_to_json

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="RSS Aggregator")
    parser.add_argument("--days", type=int, default=None, help="Показать новости за последние N дней")
    parser.add_argument("--keyword", type=str, default=None, help="Фильтр по ключевому слову (через запятую)")
    parser.add_argument("--category", type=str, default=None, help="Фильтр по категории источника")
    parser.add_argument("--sort", type=str, choices=["asc", "desc"], default=None, help="Сортировка")
    parser.add_argument("--format", type=str, choices=["json", "csv", "all"], default="all", help="Формат вывода")
    parser.add_argument("--new", action="store_true", help="Показать только новые (за сегодня)")
    args = parser.parse_args()

    sources = get_source_repository().list_all()
    print(f"Источников: {len(sources)}")

    sort_reverse = {"asc": False, "desc": True}.get(args.sort)

    articles = get_feed_service().get_feed(
        keyword=args.keyword,
        days=args.days,
        category=args.category,
        sort_reverse=sort_reverse,
        only_new=args.new,
    )

    if args.format in ("json", "all"):
        save_to_json(articles)
    if args.format in ("csv", "all"):
        save_to_csv(articles)

    print_as_table(articles)
