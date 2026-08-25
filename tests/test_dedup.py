from app.domain.dedup import deduplicate
from app.domain.models import Article


def test_deduplicate_by_link():
    articles = [
        Article(title="A", link="same", pub_date="", source_url=""),
        Article(title="B", link="same", pub_date="", source_url=""),
        Article(title="C", link="different", pub_date="", source_url=""),
    ]

    result = deduplicate(articles)

    assert len(result) == 2
