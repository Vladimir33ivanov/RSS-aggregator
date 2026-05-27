import os

import requests
import xml.etree.ElementTree as ET
from storage import save_to_json
from filters import filter_by_keyword
from cache_manager import load_cache, save_cache, is_today
from datetime import datetime
from formatter import print_as_table
from sorter import sort_news
from exporter import save_to_csv
import argparse

DEFAULT_RSS_URL = "https://news.ycombinator.com/rss"

def load_sources(filepath="sources.txt"):
    if not os.path.exists(filepath):
        return [DEFAULT_RSS_URL]
    with open(filepath, "r", encoding="utf-8") as f:
        urls = [line.strip() for line in f if line.strip() and not line.startswith("#")]
    return urls if urls else [DEFAULT_RSS_URL]

def fetch_rss(url, limit=5):
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
    except requests.exceptions.ConnectionError:
        print(f"Ошибка: не удалось подключиться к {url}")
        return []
    except requests.exceptions.Timeout:
        print(f"Ошибка: сервер не ответил за 10 секунд ({url})")
        return []
    except requests.exceptions.HTTPError as e:
        print(f"Ошибка HTTP {e.response.status_code}: {url}")
        return []

    try:
        root = ET.fromstring(response.content)
    except ET.ParseError as e:
        print(f"Ошибка: не удалось разобрать XML ({e})")
        return []

    items = root.findall(".//item")
    result = []
    for item in items[:limit]:
        title_el = item.find("title")
        link_el = item.find("link")
        date_el = item.find("pubDate")

        title = title_el.text if title_el is not None else "Без названия"
        link = link_el.text if link_el is not None else ""
        pub_date = date_el.text if date_el is not None else ""

        result.append({"title": title, "link": link, "pubDate": pub_date})

    return result


def merge_with_cache(new_items, only_new=False):
    cache = load_cache()
    today_str = datetime.now().strftime("%Y-%m-%d")

    if is_today(cache["date"]):
        existing_titles = {item["title"] for item in cache["items"]}
        unique_new = [item for item in new_items if item["title"] not in existing_titles]
        merged = cache["items"] + unique_new

        print(f"Кэш за {today_str}: добавлено {len(unique_new)} новых, всего {len(merged)}")

        save_cache(today_str, merged)

        if only_new:
            return unique_new

        return merged
    else:
        print(f"Новый день, кэш сброшен")
        save_cache(today_str, new_items)
        return new_items


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="RSS Aggregator")
    parser.add_argument("--url", type=str, default=None, help="URL RSS-фида")
    parser.add_argument("--limit", type=int, default=5, help="Кол-во новостей с каждого источника")
    parser.add_argument("--keyword", type=str, default=None, help="Фильтр по ключевому слову")
    parser.add_argument("--sort", type=str, choices=["asc", "desc"], default=None, help="Сортировка")
    parser.add_argument("--format", type=str, choices=["json", "csv", "all"], default="all", help="Формат вывода")
    parser.add_argument("--new", action="store_true", help="Показать только новые")
    args = parser.parse_args()

    urls = [args.url] if args.url else load_sources()

    news = []
    for url in urls:
        news += fetch_rss(url, args.limit)
    news = merge_with_cache(news, args.new)
    news = filter_by_keyword(news, args.keyword)

    if args.sort == "desc":
        news = sort_news(news, reverse=True)
    elif args.sort == "asc":
        news = sort_news(news)

    if args.format == "json":
        save_to_json(news)
    elif args.format == "csv":
        save_to_csv(news)
    else:
        save_to_json(news)
        save_to_csv(news)

    print_as_table(news)