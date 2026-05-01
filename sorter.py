def sort_news(news, reverse=False):
    return sorted(news, key=lambda x: x["title"], reverse=reverse)