"""
Common typings.
"""
from abc import abstractmethod
from typing import Protocol


class Comparable(Protocol):
    """Protocol for annotating comparable types."""

    @abstractmethod
    def __eq__(self, other) -> bool:
        ...

    @abstractmethod
    def __lt__(self, other) -> bool:
        ...

    @abstractmethod
    def __gt__(self, other) -> bool:
        ...


class SupportsAdd(Protocol):
    """Protocol for annotating types which support add operation."""

    @abstractmethod
    def __add__(self, other):
        ...


class SupportsSub(Protocol):
    """Protocol for annotating types which support add operation."""

    @abstractmethod
    def __sub__(self, other):
        ...
