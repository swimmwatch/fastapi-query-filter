"""
Unittests for iterators utilities.
"""
from typing import Iterable, Callable, Dict, Any, Hashable, List

import pytest

from fastapi_query_filter.utils.iter import group_by


@pytest.mark.parametrize(
    "it,func,default_factory,expected",
    [
        ([], lambda x: x, list, {}),
        ([1, 2, 3, 4], lambda x: x % 2, list, {0: [2, 4], 1: [1, 3]}),
    ],
)
def test_iter(it: Iterable, func: Callable, default_factory, expected: Dict[Hashable, List[Any]]):
    actual = group_by(it, func, default_factory)
    assert actual == expected
