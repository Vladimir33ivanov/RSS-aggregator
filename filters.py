def filter_by_keyword(news, keyword):
    if not keyword:
        return news
    return [
        item for item in news
        if keyword.lower() in item["title"].lower()
    ]

from email.utils import parsedate_to_datetime
from datetime import datetime, timezone, timedelta

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