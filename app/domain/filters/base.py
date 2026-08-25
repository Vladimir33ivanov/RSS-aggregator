"""Базовый интерфейс фильтра (Strategy pattern, см. docs/architecture-drivers.md,
сценарий качества №2 — расширяемость фильтрации)."""

from abc import ABC, abstractmethod
from typing import List

from app.domain.models import Article


class Filter(ABC):
    @abstractmethod
    def apply(self, articles: List[Article]) -> List[Article]:
        """Вернуть отфильтрованный список статей."""
        raise NotImplementedError
