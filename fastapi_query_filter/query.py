import abc
import typing

from .utils.math import IntervalType
from .types import (
    INCLUDE_OPERATORS,
    QueryFilterRequest,
    MORE_OPERATORS,
    LESS_OPERATORS,
    COMPARE_OPERATORS,
    QueryFilterOperators,
)


class BaseQuery(abc.ABC):
    @classmethod
    @abc.abstractmethod
    def interpret_value(cls, queries: QueryFilterRequest):
        """
        Interpret value from queries.
        """
        pass

    @classmethod
    @abc.abstractmethod
    def _validate_amount(cls, queries: QueryFilterRequest, value_type: typing.Type):
        """
        Validate amount queries.
        """
        pass

    @classmethod
    @abc.abstractmethod
    def _validate_operator(cls, queries: QueryFilterRequest, value_type: typing.Type):
        """
        Validate queries operator.
        """
        pass

    @classmethod
    @abc.abstractmethod
    def _validate_value_type(cls, queries: QueryFilterRequest, value_type: typing.Type):
        """
        Validate query value type.
        """
        pass

    @classmethod
    def validate(cls, queries: QueryFilterRequest, value_type: typing.Type):
        """
        Validate queries.
        """
        cls._validate_amount(queries, value_type)
        cls._validate_operator(queries, value_type)
        cls._validate_value_type(queries, value_type)


class QueryType:
    class Compare(BaseQuery):
        @classmethod
        def interpret_value(cls, queries: QueryFilterRequest):
            return queries[0].value

        @classmethod
        def _validate_amount(cls, queries: QueryFilterRequest, value_type: typing.Type):
            if len(queries) > 1:
                raise ValueError("Query with such operator type must occur only once")

        @classmethod
        def _validate_operator(cls, queries: QueryFilterRequest, value_type: typing.Type):
            query = queries[0]
            if query.operator not in COMPARE_OPERATORS:
                raise ValueError(f"Query '{query.field}' must use include operator")

        @classmethod
        def _validate_value_type(cls, queries: QueryFilterRequest, value_type: typing.Type):
            query = queries[0]
            value = cls.interpret_value(queries)
            if not isinstance(value, value_type):
                raise ValueError(f"Query '{query.field}' value has invalid type")

    class Interval(BaseQuery):
        @classmethod
        def interpret_value(cls, queries: QueryFilterRequest):
            values = [query.value for query in queries]
            return IntervalType.from_list(values)

        @classmethod
        def _validate_amount(cls, queries: QueryFilterRequest, value_type: typing.Type):
            if len(queries) != 2:
                raise ValueError("Query with such operator type must occur two times")

        @classmethod
        def _validate_operator(cls, queries: QueryFilterRequest, value_type: typing.Type):
            query_begin, query_end = sorted(queries, key=lambda query: query.value)
            if query_begin.operator not in MORE_OPERATORS or query_end.operator not in LESS_OPERATORS:
                raise ValueError("Query must be interval.")

        @classmethod
        def _validate_value_type(cls, queries: QueryFilterRequest, value_type: typing.Type):
            interval = cls.interpret_value(queries)
            if not (isinstance(interval.begin, value_type) and isinstance(interval.end, value_type)):
                raise ValueError("Query value has invalid type")

    class Include(BaseQuery):
        @classmethod
        def interpret_value(cls, queries: QueryFilterRequest):
            return queries[0].value

        @classmethod
        def _validate_amount(cls, queries: QueryFilterRequest, value_type: typing.Type):
            if len(queries) > 1:
                raise ValueError("Query with such operator type must occur only once")

        @classmethod
        def _validate_operator(cls, queries: QueryFilterRequest, value_type: typing.Type):
            query = queries[0]
            if query.operator not in INCLUDE_OPERATORS:
                raise ValueError(f"Query '{query.field}' must use include operator")

        @classmethod
        def _validate_value_type(cls, queries: QueryFilterRequest, value_type: typing.Type):
            query = queries[0]
            value = cls.interpret_value(queries)
            is_valid_type = (isinstance(val, value_type) for val in value)
            if not isinstance(value, list) or not all(is_valid_type):
                raise ValueError(f"Query '{query.field}' value has invalid type")

    class Option(BaseQuery):
        @classmethod
        def interpret_value(cls, queries: QueryFilterRequest) -> bool:
            return queries[0].value

        @classmethod
        def _validate_amount(cls, queries: QueryFilterRequest, value_type: typing.Type):
            if len(queries) > 1:
                raise ValueError("Query with such operator type must occur only once")

        @classmethod
        def _validate_operator(cls, queries: QueryFilterRequest, value_type: typing.Type):
            query = queries[0]
            if query.operator is QueryFilterOperators.OPTION:
                raise ValueError(f"Query '{query.field}' use only '{QueryFilterOperators.OPTION}' operator")

        @classmethod
        def _validate_value_type(cls, queries: QueryFilterRequest, value_type: typing.Type):
            query = queries[0]
            value = cls.interpret_value(queries)
            if not isinstance(value, bool):
                raise ValueError(f"Query '{query.field}' value has invalid type")
