from email.utils import parsedate_to_datetime
from datetime import datetime, timezone, timedelta

def filter_by_keyword(news, keyword):
    if not keyword:
        return news
    keywords = [k.strip().lower() for k in keyword.split(",")]
    return [
        item for item in news
        if any(k in item["title"].lower() for k in keywords)
    ]

def filter_by_days(news, days):
    if not days:
        return news

    cutoff = datetime.now(timezone.utc) - timedelta(days=days)
    result = []

    for item in news:
        pub_date = item.get("pubDate", "")
        if not pub_date:
            result.append(item)
            continue
        try:
            dt = parsedate_to_datetime(pub_date)
            if dt >= cutoff:
                result.append(item)
        except Exception:
            result.append(item)
        return result

def deduplicate(news):
    seen = set()
    result = []
    for item in news:
        key = item.get("link") or item.get("title")
        if key not in seen:
            seen.add(key)
            result.append(item)
    return result