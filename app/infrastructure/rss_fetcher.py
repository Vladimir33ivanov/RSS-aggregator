"""Адаптер к внешнему миру: получение и разбор RSS.

Источники опрашиваются параллельно (asyncio.gather), а не по очереди —
см. docs/architecture-drivers.md, сценарий качества №1: медленный или
зависший источник не должен задерживать всю ленту дольше собственного
таймаута. Ошибка или таймаут одного источника не должны валить остальные
(сценарий №3) — поэтому исключения ловятся отдельно на каждый fetch,
а не вокруг всего gather."""

import asyncio
import logging
import xml.etree.ElementTree as ET
from typing import List

import httpx

from app.domain.models import Article

logger = logging.getLogger(__name__)


async def fetch_source(
    client: httpx.AsyncClient, url: str, limit: int = 20, timeout: int = 10
) -> List[Article]:
    try:
        response = await client.get(url, timeout=timeout)
        response.raise_for_status()
        root = ET.fromstring(response.content)
    except httpx.HTTPError as exc:
        logger.warning("Источник %s недоступен: %s", url, exc)
        return []
    except ET.ParseError as exc:
        logger.warning("Источник %s вернул невалидный XML: %s", url, exc)
        return []

    articles: List[Article] = []
    for item in root.findall(".//item")[:limit]:
        title_el = item.find("title")
        link_el = item.find("link")
        date_el = item.find("pubDate")
        articles.append(
            Article(
                title=title_el.text if title_el is not None else "Без названия",
                link=link_el.text if link_el is not None else "",
                pub_date=date_el.text if date_el is not None else "",
                source_url=url,
            )
        )
    return articles


async def fetch_all(urls: List[str], limit: int = 20, timeout: int = 10) -> List[Article]:
    """Опрашивает все источники параллельно. Таймаут или ошибка на одном
    URL не задерживают и не отменяют остальные — fetch_source сама ловит
    свои исключения и возвращает [] вместо падения, поэтому в gather не
    нужен return_exceptions."""
    if not urls:
        return []

    async with httpx.AsyncClient() as client:
        results = await asyncio.gather(*(fetch_source(client, url, limit, timeout) for url in urls))

    articles: List[Article] = []
    for result in results:
        articles.extend(result)
    return articles
