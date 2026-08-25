"""Доменные сущности. Никаких зависимостей от FastAPI, БД или requests —
это правило слоя domain/ (см. docs/architecture-drivers.md, шаг 4)."""

from dataclasses import dataclass
from typing import Optional


@dataclass
class Source:
    id: Optional[int]
    url: str
    name: str
    category: str = "general"


@dataclass
class Article:
    title: str
    link: str
    pub_date: str
    source_url: str
