import typing
from copy import deepcopy
from itertools import chain

from sqlalchemy.sql import Select

from .utils.iter import group_by
from .definition import (
    BaseDeclarativeFilter,
    FilterType,
    QueryField,
)
from .query import QueryType
from .types import QueryFilterRequest, QueryFilterOperators, QueryFilter
from .utils.math import IntervalType
from .validation import QueryFilterValidator

_ORM_OPERATOR_TRANSFORMER = {
    QueryFilterOperators.NOT_EQ: lambda value: ("__ne__", value),
    QueryFilterOperators.EQ: lambda value: ("__eq__", value),
    QueryFilterOperators.GT: lambda value: ("__gt__", value),
    QueryFilterOperators.GE: lambda value: ("__ge__", value),
    QueryFilterOperators.IN: lambda value: ("in_", value),
    QueryFilterOperators.IS_NULL: lambda value: ("is_", None) if value is True else ("is_not", None),
    QueryFilterOperators.LT: lambda value: ("__lt__", value),
    QueryFilterOperators.LE: lambda value: ("__le__", value),
    QueryFilterOperators.LIKE: lambda value: ("like", f"%{value}%"),
    QueryFilterOperators.ILIKE: lambda value: ("ilike", f"%{value}%"),
    QueryFilterOperators.NOT: lambda value: ("is_not", value),
    QueryFilterOperators.NOT_IN: lambda value: ("not_in", value),
    QueryFilterOperators.OPTION: lambda value: ("", value),
}


class SqlQueryFilterFacade:
    def __init__(
        self,
        defined_filter: BaseDeclarativeFilter,
        queries: QueryFilterRequest,
        validate: bool = True,
    ):
        self.defined_filter = defined_filter
        self._queries = deepcopy(queries)
        self._grouped_queries = group_by(
            self._queries,
            lambda q: q.field,
            list,
        )

        self.validator = QueryFilterValidator(self.defined_filter)
        if validate:
            self.validator.validate(self._queries)

        self._values = self._extract_query_values()
        self._values_accessor = self._make_values_accessor_class()
        self.fields = self._extract_model_fields()

    @property
    def v(self):
        return self._values_accessor()

    def _make_values_accessor_class(self):
        this = self
        attrs = dict()

        # create proxy fields
        for field_name in self._values:

            def fget(self, key=field_name):
                return this._values[key]

            def fset(self, value, key=field_name):
                assert type(this._values[key]) is type(
                    value
                ), "Assignment value must have the same type as source value."

                # TODO: add value validation
                this._values[key] = value
                queries = this._grouped_queries[key]
                if isinstance(value, IntervalType):
                    query_begin, query_end = sorted(queries, key=lambda q: q.value)
                    query_begin.value = value.begin
                    query_end.value = value.end
                else:
                    queries[0].value = value

            attrs[field_name] = property(fget, fset)

        class_name = type(self.defined_filter).__name__ + "ValuesAccessor"
        values_accessor = type(class_name, (object,), attrs)
        return values_accessor

    def _extract_model_fields(self):
        return {
            field_name: field_metadata.model_field
            for field_name, field_metadata in self.defined_filter.query_fields.items()
        }

    def _extract_query_values(self) -> typing.Dict[str, typing.Any]:
        fields: typing.Dict[str, typing.Any] = {}
        for field_name, field_metadata in self.defined_filter.query_fields.items():
            curr_query_set = self._grouped_queries.get(field_name, None)
            if curr_query_set is None:
                fields[field_name] = None
            else:
                field_value = field_metadata.query_type.interpret_value(curr_query_set)
                fields[field_name] = field_value
        return fields

    def _get_orm_operator(self, operator: QueryFilterOperators, value: typing.Any):
        return _ORM_OPERATOR_TRANSFORMER[operator](value)

    def _get_orm_expression(self, model_field, operator: str, value: typing.Any):
        return getattr(model_field, operator)(value)

    def _apply_expression(self, base_stmt: Select, query: QueryFilter, query_field: QueryField):
        if isinstance(query_field.query_type, QueryType.Option):
            expression = query_field.model_field
        else:
            orm_operator, value = self._get_orm_operator(query.operator, query.value)
            expression = self._get_orm_expression(query_field.model_field, orm_operator, value)

        if query_field.filter_type is FilterType.WHERE:
            base_stmt = base_stmt.filter(expression)
        elif query_field.filter_type is FilterType.HAVING:
            base_stmt = base_stmt.having(expression)
        else:
            raise NotImplementedError(f"Unhandled condition operand type: {query_field.filter_type}")
        return base_stmt

    def apply(
        self,
        base_stmt: Select,
        exclude_fields: typing.Optional[typing.Set[str]] = None,
    ) -> Select:
        """
        Apply query filter to base statement.
        """
        exclude_fields = exclude_fields or set()
        for query in chain.from_iterable(self._grouped_queries.values()):
            if query.field in exclude_fields:
                continue

            query_field = self.defined_filter.query_fields.get(query.field, None)
            if query_field is None:
                raise ValueError(f"No such query field: {query.field}")

            base_stmt = self._apply_expression(base_stmt, query, query_field)
        return base_stmt
