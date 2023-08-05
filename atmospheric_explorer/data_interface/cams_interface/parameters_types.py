from __future__ import annotations

from atmospheric_explorer.loggers import get_logger
from pydantic.dataclasses import dataclass as pydantic_dataclass
from pydantic import computed_field, field_validator

logger = get_logger("atmexp")


@pydantic_dataclass
class Parameter:
    value: str

    def __eq__(self, other: Parameter):
        return self.value == other.value

    @computed_field
    @property
    def value_api(self) -> str:
        return self.value

    def __repr__(self) -> str:
        return f"{self.value_api}"


@pydantic_dataclass
class ListParameter:
    value: set
    base_type: type = int
    return_type: type = str
    format: str = ""

    @field_validator('value', mode='before')
    def _(cls, values: str | list[str] | set[str]):
        if isinstance(values, str):
            values = [values]
        return {cls.base_type(v) for v in values}

    @computed_field
    @property
    def value_api(self) -> str | list[str]:
        if self.return_type is str:
            return [f"{v:{self.format}}" for v in self.value]
        return [self.return_type(v) for v in self.value]

    def __eq__(self, other: ListParameter):
        return self.value == other.value

    def is_eq_superset(self, other: ListParameter):
        return (self == other) or (self.value.issuperset(other.value))

    def difference(self, other: ListParameter) -> set:
        return self.value - other.value

    def __repr__(self) -> str:
        return f"{self.value_api}"
