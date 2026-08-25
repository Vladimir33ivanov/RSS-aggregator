"""Адаптер к внешнему миру: получение и разбор RSS. Ошибка на одном источнике
не должна валить остальные — см. docs/architecture-drivers.md, сценарий качества №3."""

import logging
import xml.etree.ElementTree as ET
from typing import List

import requests

from app.domain.models import Article

logger = logging.getLogger(__name__)


def fetch_source(url: str, limit: int = 20, timeout: int = 10) -> List[Article]:
    try:
        response = requests.get(url, timeout=timeout)
        response.raise_for_status()
        root = ET.fromstring(response.content)
    except requests.exceptions.RequestException as exc:
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
