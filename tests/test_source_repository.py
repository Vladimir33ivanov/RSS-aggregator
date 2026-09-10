import os
import tempfile

import pytest

from app.infrastructure.source_repository import FileSourceRepository


@pytest.fixture
def sources_file():
    """Изолированный временный файл источников — не трогает реальный
    sources.txt проекта."""
    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".txt", mode="w", encoding="utf-8")
    tmp.close()
    yield tmp.name
    os.unlink(tmp.name)


def test_missing_file_gives_empty_repository(tmp_path):
    missing_path = str(tmp_path / "does_not_exist.txt")

    repo = FileSourceRepository(path=missing_path)

    assert repo.list_all() == []


def test_load_reads_urls_skipping_blank_lines_and_comments(sources_file):
    with open(sources_file, "w", encoding="utf-8") as f:
        f.write("https://a.example/rss\n")
        f.write("\n")
        f.write("# комментарий, не источник\n")
        f.write("https://b.example/rss\n")

    repo = FileSourceRepository(path=sources_file)
    urls = {s.url for s in repo.list_all()}

    assert urls == {"https://a.example/rss", "https://b.example/rss"}


def test_loaded_sources_default_to_general_category(sources_file):
    with open(sources_file, "w", encoding="utf-8") as f:
        f.write("https://a.example/rss\n")

    repo = FileSourceRepository(path=sources_file)

    assert repo.list_all()[0].category == "general"


def test_add_appends_to_memory_and_to_file(sources_file):
    repo = FileSourceRepository(path=sources_file)

    added = repo.add("https://new.example/rss", name="New", category="tech")

    assert added in repo.list_all()
    with open(sources_file, "r", encoding="utf-8") as f:
        assert "https://new.example/rss" in f.read()


def test_add_and_reload_persists_across_instances(sources_file):
    repo = FileSourceRepository(path=sources_file)
    repo.add("https://persisted.example/rss", name="Persisted")

    reloaded = FileSourceRepository(path=sources_file)

    assert any(s.url == "https://persisted.example/rss" for s in reloaded.list_all())


def test_list_by_category_filters_correctly(sources_file):
    repo = FileSourceRepository(path=sources_file)
    repo.add("https://tech.example/rss", name="Tech", category="tech")
    repo.add("https://sport.example/rss", name="Sport", category="sport")

    tech_sources = repo.list_by_category("tech")

    assert len(tech_sources) == 1
    assert tech_sources[0].url == "https://tech.example/rss"


def test_ids_are_unique_and_increment(sources_file):
    repo = FileSourceRepository(path=sources_file)
    first = repo.add("https://one.example/rss", name="One")
    second = repo.add("https://two.example/rss", name="Two")

    assert first.id != second.id


def test_delete_removes_from_memory_and_file(sources_file):
    repo = FileSourceRepository(path=sources_file)
    to_keep = repo.add("https://keep.example/rss", name="Keep")
    to_delete = repo.add("https://delete.example/rss", name="Delete")

    result = repo.delete(to_delete.id)

    assert result is True
    remaining_urls = {s.url for s in repo.list_all()}
    assert remaining_urls == {to_keep.url}
    with open(sources_file, "r", encoding="utf-8") as f:
        content = f.read()
    assert "delete.example" not in content
    assert "keep.example" in content


def test_delete_unknown_id_returns_false(sources_file):
    repo = FileSourceRepository(path=sources_file)

    assert repo.delete(999) is False
