import requests
import xml.etree.ElementTree as ET
import sys
from storage import save_to_json
from filters import filter_by_keyword
from cache_manager import load_cache, save_cache, is_today
from datetime import datetime
from formatter import print_as_table
from sorter import sort_news
from exporter import save_to_csv

DEFAULT_RSS_URL = "https://news.ycombinator.com/rss"


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
    url = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_RSS_URL
    limit = int(sys.argv[3]) if len(sys.argv) > 3 else 5
    keyword = sys.argv[2] if len(sys.argv) > 2 else None
    sort_order = sys.argv[4] if len(sys.argv) > 4 else None
    format_type = sys.argv[5] if len(sys.argv) > 5 else "all"
    only_new = "--new" in sys.argv

    if format_type not in["json", "csv", "all"]:
        print("Incorrect format, using all")
        format_type = "all"

    news = fetch_rss(url, limit)
    news = merge_with_cache(news, only_new)
    news = filter_by_keyword(news, keyword)

    if sort_order == "desc":
        news = sort_news(news, reverse=True)
    elif sort_order == "asc":
        news = sort_news(news)

    if format_type == "json":
        save_to_json(news)
    elif format_type == "csv":
        save_to_csv(news)
    else:
        save_to_json(news)
        save_to_csv(news)

    print_as_table(news)
