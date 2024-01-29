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
    def __init__(self, value_type: typing.Type):
        self.value_type = value_type

    @abc.abstractmethod
    def interpret_value(self, queries: QueryFilterRequest):
        """
        Interpret value from queries.
        """
        pass

    @abc.abstractmethod
    def _validate_amount(self, queries: QueryFilterRequest):
        """
        Validate amount queries.
        """
        pass

    @abc.abstractmethod
    def _validate_operator(self, queries: QueryFilterRequest):
        """
        Validate queries operator.
        """
        pass

    @abc.abstractmethod
    def _validate_value_type(self, queries: QueryFilterRequest):
        """
        Validate query value type.
        """
        pass

    def validate(self, queries: QueryFilterRequest):
        """
        Validate queries.
        """
        self._validate_amount(queries)
        self._validate_operator(queries)
        self._validate_value_type(queries)


class QueryType:
    class Compare(BaseQuery):
        def interpret_value(self, queries: QueryFilterRequest):
            return queries[0].value

        def _validate_amount(self, queries: QueryFilterRequest):
            query = queries[0]
            if len(queries) > 1:
                raise ValueError(f"Query '{query.field}' with such operator type must occur only once")

        def _validate_operator(self, queries: QueryFilterRequest):
            query = queries[0]
            if query.operator not in COMPARE_OPERATORS:
                raise ValueError(f"Query '{query.field}' must use include operator")

        def _validate_value_type(self, queries: QueryFilterRequest):
            query = queries[0]
            value = self.interpret_value(queries)
            if not isinstance(value, self.value_type):
                raise ValueError(f"Query '{query.field}' value has invalid type")

    class Interval(BaseQuery):
        def interpret_value(self, queries: QueryFilterRequest):
            values = [query.value for query in queries]
            return IntervalType.from_list(values)

        def _validate_amount(self, queries: QueryFilterRequest):
            query = queries[0]
            if len(queries) != 2:
                raise ValueError(f"Query '{query.field}' with such operator type must occur two times")

        def _validate_operator(self, queries: QueryFilterRequest):
            query_begin, query_end = sorted(queries, key=lambda query: query.value)
            if query_begin.operator not in MORE_OPERATORS or query_end.operator not in LESS_OPERATORS:
                raise ValueError(f"Query {query_begin.field} must be interval.")

        def _validate_value_type(self, queries: QueryFilterRequest):
            query = queries[0]
            try:
                _ = self.interpret_value(queries)
            except ValueError:
                raise ValueError(f"Query '{query.field}' value has invalid type")

    class Include(BaseQuery):
        def interpret_value(self, queries: QueryFilterRequest):
            return queries[0].value

        def _validate_amount(self, queries: QueryFilterRequest):
            query = queries[0]
            if len(queries) > 1:
                raise ValueError(f"Query {query} with such operator type must occur only once")

        def _validate_operator(self, queries: QueryFilterRequest):
            query = queries[0]
            if query.operator not in INCLUDE_OPERATORS:
                raise ValueError(f"Query '{query.field}' must use include operator")

        def _validate_value_type(self, queries: QueryFilterRequest):
            query = queries[0]
            value = self.interpret_value(queries)
            is_valid_type = (isinstance(val, self.value_type) for val in value)
            if not isinstance(value, list) or not all(is_valid_type):
                raise ValueError(f"Query '{query.field}' value has invalid type")

    class Option(BaseQuery):
        def interpret_value(self, queries: QueryFilterRequest) -> bool:
            return queries[0].value

        def _validate_amount(self, queries: QueryFilterRequest):
            query = queries[0]
            if len(queries) > 1:
                raise ValueError(f"Query {query.field} with such operator type must occur only once")

        def _validate_operator(self, queries: QueryFilterRequest):
            query = queries[0]
            if query.operator is QueryFilterOperators.OPTION:
                raise ValueError(f"Query '{query.field}' use only '{QueryFilterOperators.OPTION}' operator")

        def _validate_value_type(self, queries: QueryFilterRequest):
            query = queries[0]
            value = self.interpret_value(queries)
            if not isinstance(value, bool):
                raise ValueError(f"Query '{query.field}' value has invalid type")
