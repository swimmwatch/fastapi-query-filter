"""
Constants and typings.
"""
import enum
import typing
from datetime import datetime

from pydantic import BaseModel, validator

QueryFilterValueType = typing.Any


class QueryFilterOperators(str, enum.Enum):
    IS_NULL = "isnull"
    LIKE = "like"
    ILIKE = "ilike"
    NOT_IN = "not_in"
    IN = "in"
    LT = "<"
    LE = "<="
    GT = ">"
    GE = ">="
    EQ = "=="
    NOT_EQ = "!="
    NOT = "not"
    OPTION = "option"


INCLUDE_OPERATORS = {
    QueryFilterOperators.IN,
    QueryFilterOperators.NOT_IN,
}
LESS_OPERATORS = {
    QueryFilterOperators.LT,
    QueryFilterOperators.LE,
}
MORE_OPERATORS = {
    QueryFilterOperators.GT,
    QueryFilterOperators.GE,
}
COMPARE_OPERATORS = {
    QueryFilterOperators.EQ,
    QueryFilterOperators.NOT_EQ,
    QueryFilterOperators.LT,
    QueryFilterOperators.LE,
    QueryFilterOperators.GT,
    QueryFilterOperators.GE,
    QueryFilterOperators.LIKE,
    QueryFilterOperators.ILIKE,
    QueryFilterOperators.IS_NULL,
}


class QueryFilter(BaseModel):
    field: str
    operator: QueryFilterOperators
    value: QueryFilterValueType

    class Config:
        use_enum_values = True

    @validator("field")
    def check_field(cls, val):
        if not val:
            raise ValueError("Field value must be not empty")
        return val

    @validator("operator")
    def check_operator(cls, val):
        available_operators = {member for member in QueryFilterOperators}

        if val not in available_operators:
            raise ValueError(f"Invalid operator. It must be from {QueryFilterOperators}")

        return val

    @validator("value")
    def parse_value_type(cls, val):
        """
        Parse appropriate types for value field.
        """
        if isinstance(val, str):
            # try parse datetime from string
            try:
                val = datetime.strptime(val, "%Y-%m-%d %H:%M:%S")
                return val
            except ValueError:
                pass

            # try parse time from string
            try:
                val = datetime.strptime(val, "%H:%M:%S").time()
                return val
            except ValueError:
                pass

            # try parse date from string
            try:
                val = datetime.strptime(val, "%Y-%m-%d").date()
                return val
            except ValueError:
                pass

        return val


SqlQueryFilterType = typing.List[QueryFilter]
ValidatorHandler = typing.Callable[[object, QueryFilter], None]


class Validator(typing.NamedTuple):
    field_name: str
    func: ValidatorHandler
