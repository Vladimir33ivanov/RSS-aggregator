import json
from datetime import datetime

def save_to_json(data, filename="news.json"):
    output = {
        "timestamp": datetime.now().isoformat(),
        "count": len(data),
        "items": data
    }
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=4)