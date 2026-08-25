from app.domain.filters.keyword_filter import KeywordFilter
from app.domain.models import Article


def test_keyword_filter_matches_title():
    articles = [
        Article(title="Python news", link="", pub_date="", source_url=""),
        Article(title="Other topic", link="", pub_date="", source_url=""),
    ]

    result = KeywordFilter("python").apply(articles)

    assert len(result) == 1
    assert result[0].title == "Python news"


def test_keyword_filter_supports_multiple_keywords():
    articles = [
        Article(title="Python news", link="", pub_date="", source_url=""),
        Article(title="Go news", link="", pub_date="", source_url=""),
        Article(title="Other topic", link="", pub_date="", source_url=""),
    ]

    result = KeywordFilter("python, go").apply(articles)

    assert {a.title for a in result} == {"Python news", "Go news"}


def test_keyword_filter_empty_keyword_returns_all():
    articles = [Article(title="Anything", link="", pub_date="", source_url="")]

    result = KeywordFilter("").apply(articles)

    assert result == articles
