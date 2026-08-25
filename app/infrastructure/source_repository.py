"""Repository pattern поверх хранилища источников. Перенесено из логики
load_sources() в старом main.py — источники по-прежнему читаются из
sources.txt, чтобы не терять уже накопленный список. Интерфейс не завязан
на конкретное хранилище (см. docs/architecture-drivers.md), поэтому замена
на SQLite в будущем не потребует правок в FeedService/API."""

import os
from typing import List

from app.domain.models import Source

DEFAULT_SOURCES_FILE = "sources.txt"


class FileSourceRepository:
    def __init__(self, path: str = DEFAULT_SOURCES_FILE):
        self._path = path
        self._sources: List[Source] = []
        self._next_id = 1
        self._load()

    def _load(self) -> None:
        if not os.path.exists(self._path):
            return
        with open(self._path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("#"):
                    continue
                self._sources.append(
                    Source(id=self._next_id, url=line, name=line, category="general")
                )
                self._next_id += 1

    def add(self, url: str, name: str, category: str = "general") -> Source:
        source = Source(id=self._next_id, url=url, name=name, category=category)
        self._sources.append(source)
        self._next_id += 1
        with open(self._path, "a", encoding="utf-8") as f:
            f.write(f"{url}\n")
        return source

    def list_all(self) -> List[Source]:
        return list(self._sources)

    def list_by_category(self, category: str) -> List[Source]:
        return [s for s in self._sources if s.category == category]
