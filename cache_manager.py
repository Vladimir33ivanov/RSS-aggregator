import json
import os
from datetime import datetime

CACHE_FILE = "news_cache.json"

def load_cache():
    if os.path.exists(CACHE_FILE):
        with open(CACHE_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {"date": None, "items": []}

def save_cache(date, items):
    with open(CACHE_FILE, "w", encoding="utf-8") as f:
        json.dump({"date": date, "items": items}, f, ensure_ascii=False, indent=4)

def is_today(date_str):
    return date_str == datetime.now().strftime("%Y-%m-%d")