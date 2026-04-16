def filter_by_keyword(news, keyword):
    if not keyword:
        return news

    return [
        item for item in news
        if keyword.lower() in item["title"].lower()
    ]