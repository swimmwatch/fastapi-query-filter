"""
Common typings.
"""
from abc import abstractmethod
from typing import Protocol, TypeVar, Any


class Comparable(Protocol):
    """Protocol for annotating comparable types."""

    @abstractmethod
    def __lt__(self, other: Any) -> bool:
        ...


CT = TypeVar("CT", bound=Comparable)
