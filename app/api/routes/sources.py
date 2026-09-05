from typing import Optional

from fastapi import APIRouter, Depends
from pydantic import BaseModel

from app.dependencies import get_source_repository
from app.infrastructure.source_repository import FileSourceRepository

router = APIRouter(prefix="/sources", tags=["sources"])


class SourceIn(BaseModel):
    url: str
    name: str
    category: str = "general"


@router.get("")
def list_sources(
    category: Optional[str] = None,
    repo: FileSourceRepository = Depends(get_source_repository),
):
    if category:
        return repo.list_by_category(category)
    return repo.list_all()


@router.post("")
def add_source(
    source: SourceIn,
    repo: FileSourceRepository = Depends(get_source_repository),
):
    return repo.add(source.url, source.name, source.category)
