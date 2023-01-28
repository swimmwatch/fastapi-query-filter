import abc
import typing

from .utils.math import IntervalType
from .types import (
    INCLUDE_OPERATORS,
    QueryFilter,
    SqlQueryFilterType,
    MORE_OPERATORS,
    LESS_OPERATORS,
    COMPARE_OPERATORS,
    QueryFilterOperators,
)


class BaseQuery(abc.ABC):
    @classmethod
    @abc.abstractmethod
    def interpret_value(cls, queries: SqlQueryFilterType):
        """
        Interpret value from queries.
        """
        pass

    @classmethod
    @abc.abstractmethod
    def validate(cls, queries: SqlQueryFilterType, value_type: typing.Type):
        """
        Validate queries with common operator.
        """
        pass


class QueryType:
    class Compare(BaseQuery):
        @classmethod
        def interpret_value(cls, queries: SqlQueryFilterType):
            return queries[0].value

        @classmethod
        def validate(cls, queries: typing.List[QueryFilter], value_type: typing.Type):
            if len(queries) > 1:
                raise ValueError("Query with such operator type must occur only once")

            query = queries[0]
            if query.operator not in COMPARE_OPERATORS:
                raise ValueError(f"Query '{query.field}' must use include operator")

            value = cls.interpret_value(queries)
            if not isinstance(value, value_type):
                raise ValueError(f"Query '{query.field}' value has invalid type")

    class Interval(BaseQuery):
        @classmethod
        def interpret_value(cls, queries: SqlQueryFilterType):
            values = [query.value for query in queries]
            return IntervalType.from_list(values)

        @classmethod
        def validate(cls, queries: typing.List[QueryFilter], value_type: typing.Type):
            if len(queries) != 2:
                raise ValueError("Query with such operator type must occur two times")

            interval = cls.interpret_value(queries)

            query_begin, query_end = sorted(queries, key=lambda query: query.value)

            if query_begin.operator not in MORE_OPERATORS or query_end.operator not in LESS_OPERATORS:
                raise ValueError("Query must be interval.")

            if not (isinstance(interval.begin, value_type) and isinstance(interval.end, value_type)):
                raise ValueError("Query value has invalid type")

    class Include(BaseQuery):
        @classmethod
        def interpret_value(cls, queries: SqlQueryFilterType):
            return queries[0].value

        @classmethod
        def validate(cls, queries: typing.List[QueryFilter], value_type: typing.Type):
            if len(queries) > 1:
                raise ValueError("Query with such operator type must occur only once")

            query = queries[0]
            if query.operator not in INCLUDE_OPERATORS:
                raise ValueError(f"Query '{query.field}' must use include operator")

            value = cls.interpret_value(queries)
            is_valid_type = (isinstance(val, value_type) for val in value)
            if not isinstance(value, list) or not all(is_valid_type):
                raise ValueError(f"Query '{query.field}' value has invalid type")

    class Option(BaseQuery):
        @classmethod
        def interpret_value(cls, queries: SqlQueryFilterType) -> bool:
            return queries[0].value

        @classmethod
        def validate(cls, queries: typing.List[QueryFilter], value_type: typing.Type):
            if len(queries) > 1:
                raise ValueError("Query with such operator type must occur only once")

            query = queries[0]
            if query.operator is QueryFilterOperators.OPTION:
                raise ValueError(f"Query '{query.field}' use only '{QueryFilterOperators.OPTION}' operator")

            value = cls.interpret_value(queries)
            if not isinstance(value, bool):
                raise ValueError(f"Query '{query.field}' value has invalid type")
