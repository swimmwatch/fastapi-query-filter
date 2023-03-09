"""
Unittests for math utilities.
"""
from datetime import timedelta, date
from typing import List

import pytest

from fastapi_query_filter.utils.math import IntervalType, CT


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
        ([date(2020, 1, 1), date(2020, 1, 2)], IntervalType(date(2020, 1, 1), date(2020, 1, 2))),
    ],
)
def test_interval_from_xs(xs: List, expected: IntervalType) -> None:
    actual = IntervalType.from_list(xs)
    assert actual == expected


@pytest.mark.parametrize(
    "interval,add,expected",
    [
        (IntervalType(1, 2), 1, IntervalType(2, 3)),
        (IntervalType(1, 2), -1, IntervalType(0, 1)),
        (
            IntervalType(date(2020, 1, 1), date(2020, 1, 2)),
            timedelta(days=1),
            IntervalType(date(2020, 1, 2), date(2020, 1, 3)),
        ),
        (
            IntervalType(date(2020, 1, 1), date(2020, 1, 2)),
            -timedelta(days=1),
            IntervalType(date(2019, 12, 31), date(2020, 1, 1)),
        ),
    ],
)
def test_interval_add(interval: IntervalType, add: CT, expected: IntervalType) -> None:
    actual = interval + add
    assert actual == expected
