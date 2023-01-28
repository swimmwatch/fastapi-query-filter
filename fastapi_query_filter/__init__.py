import typing

from sqlalchemy.sql import Select

from .utils.iter import group_by
from .definition import (
    BaseDeclarativeFilter,
    FilterType,
    QueryField,
)
from .query import QueryType
from .types import QueryFilterRequest, QueryFilterOperators
from .validation import QueryFilterValidator


class SqlQueryFilterFacade:
    _orm_operator_transformer = {
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

    def __init__(
        self,
        defined_filter: BaseDeclarativeFilter,
        queries: QueryFilterRequest,
        validate: bool = True,
    ):
        self.defined_filter = defined_filter
        self.queries = queries

        self.validator = QueryFilterValidator(self.defined_filter)
        if validate:
            self.validator.validate(self.queries)

        self.values = self._extract_query_values(self.queries)
        self.fields = self._extract_model_fields()

    def _extract_model_fields(self):
        return {
            field_name: field_metadata.model_field
            for field_name, field_metadata in self.defined_filter.query_fields.items()
        }

    def _extract_query_values(self, queries: QueryFilterRequest) -> typing.Dict[str, typing.Any]:
        grouped_queries = group_by(
            queries,
            lambda query: query.field,
            list,
        )
        fields: typing.Dict[str, typing.Any] = {}
        for field_name, field_metadata in self.defined_filter.query_fields.items():
            curr_query_set = grouped_queries.get(field_name, None)
            if curr_query_set is None:
                fields[field_name] = None
            else:
                field_value = field_metadata.query_type.interpret_value(curr_query_set)
                fields[field_name] = field_value
        return fields

    def _get_orm_operator(self, operator: QueryFilterOperators, value: typing.Any):
        return self._orm_operator_transformer[operator](value)

    def _get_orm_expression(self, model_field, operator: str, value: typing.Any):
        return getattr(model_field, operator)(value)

    def _apply_expression(self, base_stmt, expression, query_field: QueryField):
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
        for query in self.queries:
            if query.field in exclude_fields:
                continue

            query_field = self.defined_filter.query_fields.get(query.field, None)
            if query_field is None:
                raise ValueError(f"No such query field: {query.field}")

            if isinstance(query_field.query_type, QueryType.Option):
                _, value = self._get_orm_operator(query.operator, query.value)
                if value:
                    expression = query_field.model_field
                    base_stmt = self._apply_expression(base_stmt, expression, query_field)
            else:
                operator, value = self._get_orm_operator(query.operator, query.value)
                expression = self._get_orm_expression(query_field.model_field, operator, value)
                base_stmt = self._apply_expression(base_stmt, expression, query_field)

        return base_stmt
