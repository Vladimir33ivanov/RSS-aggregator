import tempfile

from fastapi.testclient import TestClient

from app.dependencies import get_source_repository
from app.infrastructure.source_repository import FileSourceRepository
from app.main import app


_tmp_sources_file = tempfile.NamedTemporaryFile(delete=False, suffix=".txt")
_tmp_sources_file.close()
_test_repository = FileSourceRepository(path=_tmp_sources_file.name)


def _test_source_repository() -> FileSourceRepository:
    """Один и тот же временный репозиторий на весь тестовый прогон, чтобы не
    писать в реальный sources.txt проекта и чтобы данные не терялись между
    запросами внутри одного теста."""
    return _test_repository


app.dependency_overrides[get_source_repository] = _test_source_repository

client = TestClient(app)


def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_add_and_list_sources():
    response = client.post(
        "/sources",
        json={"url": "https://example.com/rss", "name": "Example", "category": "tech"},
    )
    assert response.status_code == 200

    response = client.get("/sources")
    assert response.status_code == 200
    assert any(s["url"] == "https://example.com/rss" for s in response.json())
