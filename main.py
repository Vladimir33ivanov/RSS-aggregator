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
    response = requests.get(url)
    root = ET.fromstring(response.content)
    items = root.findall(".//item")
    result = []

    for item in items[:limit]:
        title = item.find("title").text
        link = item.find("link").text
        result.append({"title": title, "link": link})

    return result


def merge_with_cache(new_items):
    cache = load_cache()
    today_str = datetime.now().strftime("%Y-%m-%d")

    if is_today(cache["date"]):
        existing_titles = {item["title"] for item in cache["items"]}
        unique_new = [item for item in new_items if item["title"] not in existing_titles]
        merged = cache["items"] + unique_new
        print(f"Кэш за {today_str}: добавлено {len(unique_new)} новых, всего {len(merged)}")
    else:
        merged = new_items
        print(f"Новый день, кэш сброшен")

    save_cache(today_str, merged)
    return merged


if __name__ == "__main__":
    url = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_RSS_URL
    limit = int(sys.argv[3]) if len(sys.argv) > 3 else 5
    keyword = sys.argv[2] if len(sys.argv) > 2 else None
    sort_order = sys.argv[4] if len(sys.argv) > 4 else None

    news = fetch_rss(url, limit)
    news = merge_with_cache(news)
    news = filter_by_keyword(news, keyword)

    if sort_order == "desc":
        news = sort_news(news, reverse=True)
    elif sort_order == "asc":
        news = sort_news(news)

    save_to_json(news) #JSON формат
    save_to_csv(news) #CSV формат

    print_as_table(news)
