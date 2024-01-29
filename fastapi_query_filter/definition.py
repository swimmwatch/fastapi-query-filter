import typing
from collections import defaultdict
from enum import Enum, auto

from .query import BaseQuery
from .types import ValidatorHandler, Validator


class FilterType(Enum):
    WHERE = auto()
    HAVING = auto()


class QueryField:
    """
    Query filter field metadata. It's used for filter definition.
    """

    def __init__(
        self,
        query_type: BaseQuery,
        model_field,
        filter_type: FilterType = FilterType.WHERE,
    ):
        self.query_type = query_type
        self.model_field = model_field
        self.filter_type = filter_type


class BaseDeclarativeFilter:
    def __init__(self):
        self._user_defined_fields = self._get_user_defined_fields()
        self.query_fields = self._get_defined_query_fields(self._user_defined_fields)
        self.query_fields_validators = self._get_defined_query_validators(self._user_defined_fields)

    def _get_user_defined_fields(self) -> typing.Dict[str, typing.Any]:
        """
        Returns user defined class fields.
        """
        return {
            attr_name: self.__class__.__dict__[attr_name]
            for attr_name in dir(self.__class__)
            if not attr_name.startswith("_")
        }

    def _get_defined_query_validators(
        self, user_defined_fields
    ) -> typing.DefaultDict[str, typing.List[ValidatorHandler]]:
        """
        Returns defined query validators.
        """
        validators = (field_value for field_value in user_defined_fields.values() if isinstance(field_value, Validator))
        query_validators = defaultdict(list)
        for validator in validators:
            field_name, func = validator
            query_validators[field_name].append(func)

        return query_validators

    def _get_defined_query_fields(self, user_defined_fields) -> typing.Dict[str, QueryField]:
        return {
            field_name: field_value
            for field_name, field_value in user_defined_fields.items()
            if isinstance(field_value, QueryField)
        }
