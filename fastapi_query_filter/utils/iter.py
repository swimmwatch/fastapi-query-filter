"""
Utilities for iterators.
"""
from collections import defaultdict, deque
from itertools import tee, filterfalse
from typing import (
    TypeVar,
    Callable,
    Iterable,
    Tuple,
    DefaultDict,
    Any,
    Type,
    MutableSequence,
)

T = TypeVar("T")


def group_by(
    it: Iterable[T],
    func: Callable[[T], Any],
    default_factory: Type[MutableSequence[T]] = deque,
) -> DefaultDict[Any, MutableSequence[T]]:
    """
    Group by elements in collection by func (Works similar as SQL GROUP BY statement).
    :param it: Iterable
    :param func: Function that extracts value
    :param default_factory: Default factory
    """
    acc: DefaultDict[Any, MutableSequence[T]] = defaultdict(default_factory)
    for i in it:
        val = func(i)
        acc[val].append(i)
    return acc
