from typing import Optional

from fastapi import APIRouter, Depends, Query

from app.dependencies import get_feed_service
from app.services.feed_service import FeedService

router = APIRouter(prefix="/feed", tags=["feed"])


@router.get("")
def get_feed(
    keyword: Optional[str] = Query(default=None),
    days: Optional[int] = Query(default=None),
    sort: Optional[str] = Query(default=None, description="asc или desc"),
    feed_service: FeedService = Depends(get_feed_service),
):
    sort_reverse = {"asc": False, "desc": True}.get(sort)
    return feed_service.get_feed(keyword=keyword, days=days, sort_reverse=sort_reverse)
