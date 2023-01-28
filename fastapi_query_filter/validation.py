import typing

from .utils.iter import group_by
from .types import SqlQueryFilterType
from .definition import QueryField, BaseDeclarativeFilter
from .types import QueryFilter, Validator, ValidatorHandler


def bind_validator(field_name: str):
    """
    Decorator for binding query field validator into filter definition.
    """

    def wrapper(func) -> typing.Tuple[str, ValidatorHandler]:
        """
        Returns field name and validator handler.
        """
        return Validator(field_name, func)

    return wrapper


class QueryFilterValidator:
    def __init__(self, defined_filter: BaseDeclarativeFilter):
        self.defined_filter = defined_filter

    def _call_user_validators(
        self, passed_field_name: str, queries: typing.Iterable[QueryFilter]
    ):
        validators = self.defined_filter.query_fields_validators.get(passed_field_name, None)
        if validators is None:
            return

        for validator in validators:
            for query in queries:
                validator(self.defined_filter, query)

    def _call_query_type_validator(
        self,
        query_field_metadata: QueryField,
        queries: typing.List[QueryFilter],
    ):
        query_field_metadata.query_type.validate(
            queries, query_field_metadata.value_type
        )

    def validate(self, queries: SqlQueryFilterType):
        """
        Validate passed query filter.
        """
        grouped_queries = group_by(
            queries,
            lambda query: query.field,
            list,
        )
        for passed_field_name, curr_query_set in grouped_queries.items():
            query_field_metadata: typing.Optional[
                QueryField
            ] = self.defined_filter.query_fields.get(passed_field_name, None)
            if query_field_metadata is None:
                raise ValueError(f"Not defined query field: {passed_field_name}")

            self._call_query_type_validator(query_field_metadata, curr_query_set)  # type: ignore
            self._call_user_validators(passed_field_name, curr_query_set)
