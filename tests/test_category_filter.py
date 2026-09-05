from app.domain.filters.category_filter import CategoryFilter
from app.domain.models import Article


def test_category_filter_keeps_only_matching_source_urls():
    articles = [
        Article(title="Tech 1", link="1", pub_date="", source_url="https://tech.example/rss"),
        Article(title="News 1", link="2", pub_date="", source_url="https://news.example/rss"),
    ]

    result = CategoryFilter(["https://tech.example/rss"]).apply(articles)

    assert len(result) == 1
    assert result[0].title == "Tech 1"


def test_category_filter_empty_urls_returns_all():
    articles = [Article(title="Anything", link="", pub_date="", source_url="")]

    result = CategoryFilter([]).apply(articles)

    assert result == articles
