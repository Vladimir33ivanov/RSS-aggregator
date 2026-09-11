from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from app.dependencies import get_source_repository
from app.infrastructure.source_repository import DuplicateSourceError, FileSourceRepository

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
    try:
        return repo.add(source.url, source.name, source.category)
    except DuplicateSourceError as exc:
        raise HTTPException(status_code=409, detail=str(exc))


@router.delete("/{source_id}")
def delete_source(
    source_id: int,
    repo: FileSourceRepository = Depends(get_source_repository),
):
    deleted = repo.delete(source_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Источник не найден")
    return {"status": "deleted", "id": source_id}
