"""
Unittests for math utilities.
"""
from typing import List

import pytest

from fastapi_query_filter.utils.math import IntervalType


@pytest.mark.parametrize(
    "begin,end",
    [
        (1, 2),
        (1, 1),
    ],
)
def test_interval_type_positive_cases(begin, end) -> None:
    try:
        _ = IntervalType(begin, end)
    except ValueError:
        pytest.xfail("")


@pytest.mark.parametrize(
    "begin,end",
    [
        (1, 2),
        (1, 1),
    ],
)
def test_interval_type_negative_cases(begin, end):
    try:
        _ = IntervalType(begin, end)
    except ValueError as err:
        pytest.xfail(err)


@pytest.mark.parametrize(
    "xs,expected",
    [
        ([1, 2], IntervalType(1, 2)),
        (["1", "2"], IntervalType("1", "2")),
    ],
)
def test_interval_from_xs(xs: List, expected: IntervalType) -> None:
    actual = IntervalType.from_list(xs)
    assert actual == expected
