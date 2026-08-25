"""Перенесено из formatter.py (print_as_table). Живёт отдельно от domain/
infrastructure — это презентация, специфичная только для терминала."""

from datetime import datetime
from typing import List

from app.domain.models import Article


def print_as_table(articles: List[Article]) -> None:
    if not articles:
        print("Новостей не найдено")
        return

    print("\n" + "=" * 80)
    print(f"Rss news | {datetime.now().strftime('%d.%m.%Y %H:%M')}")
    print("=" * 80)

    for i, article in enumerate(articles, start=1):
        title = article.title[:55] + "..." if len(article.title) > 55 else article.title
        print(f"{i:>2}. {title}")
        if article.pub_date:
            print(f"     \U0001F4C5 {article.pub_date}")
        print(f"     \U0001F517 {article.link}")
        print("-" * 80)

    print(f"\U0001F4CA Всего: {len(articles)} новостей\n")
