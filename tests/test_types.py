from datetime import time, date, datetime
from typing import Any

import pytest

from fastapi_query_filter.types import QueryFilter, QueryFilterOperators


@pytest.mark.parametrize(
    "input_value,expected_value",
    [
        ("", ""),
        ("some string", "some string"),
        (1, 1),
        (1.0, 1.0),
        ([], []),
        ("23:59:59", time(23, 59, 59)),
        ("1970-01-01", date(1970, 1, 1)),
        ("1970-01-01 23:59:59", datetime(1970, 1, 1, 23, 59, 59)),
    ],
)
def test_query_filter_interpret_value(input_value: Any, expected_value: Any):
    q = QueryFilter(
        field="test",
        operator=QueryFilterOperators.EQ,
        value=input_value,
    )
    assert q.value == expected_value
    assert type(q.value) is type(expected_value)
