from __future__ import annotations

from atmospheric_explorer.loggers import get_logger
from pydantic.dataclasses import dataclass as pydantic_dataclass
from pydantic import computed_field, field_validator, model_validator
from typing import Any
from datetime import datetime

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
class SetParameter:
    value: set
    format_str: str = ""

    @field_validator('value', mode="before")
    def _(cls, val):
        if not (isinstance(val, list) or isinstance(val, set)):
            val = [val]
        return set(val)

    @computed_field
    @property
    def value_api(self) -> list[str]:
        return sorted([f"{v:{self.format_str}}" for v in self.value])

    def __eq__(self, other: SetParameter):
        return self.value == other.value

    def is_eq_superset(self, other: SetParameter):
        return (self == other) or (self.value.issuperset(other.value))

    def difference(self, other: SetParameter) -> SetParameter:
        return SetParameter(self.value - other.value)

    def __repr__(self) -> str:
        return f"{self.value_api}"

    def __iter__(self):
        return iter(self.value)


@pydantic_dataclass
class AreaParameter:
    north: int
    west: int
    south: int
    east: int

    @model_validator(mode='before')
    @classmethod
    def modify_input(cls, data: list[int]) -> Any:
        data = data.args[0]
        data = {
            "north": data[0],
            "west": data[1],
            "south": data[2],
            "east": data[3]
        }
        return data

    @model_validator(mode='after')
    def check_dates(self) -> DateIntervalParameter:
        if self.north < self.south:
            raise ValueError("North is lower than south!")
        if self.west < self.east:
            raise ValueError("West is lower than east!")
        return self

    @computed_field
    @property
    def value_api(self) -> list[str]:
        return [self.north, self.west, self.south, self.east]

    def __eq__(self, other: AreaParameter):
        return self.value == other.value

    def is_eq_superset(self, other: AreaParameter):
        return (self == other) or (set(self.value).issuperset(set(other.value)))

    def difference(self, other: AreaParameter) -> AreaParameter:
        return AreaParameter(self.value - other.value)

    def __repr__(self) -> str:
        return f"{self.value_api}"

    def __iter__(self):
        return iter(self.value)

@pydantic_dataclass
class DateIntervalParameter:
    start: datetime
    end: datetime
    
    @model_validator(mode='before')
    @classmethod
    def modify_input(cls, data: Any) -> Any:
        data = data.args[0].strip().split("/")
        data = {
            "start": datetime.strptime(data[0], '%Y-%m-%d'),
            "end": datetime.strptime(data[1], '%Y-%m-%d')
        }
        return data

    @model_validator(mode='after')
    def check_dates(self) -> DateIntervalParameter:
        if self.end < self.start:
            raise ValueError("Start is more recent than end!")
        return self

    @computed_field
    @property
    def value_api(self) -> list[str]:
        return f"{self.start}/{self.end}"

    def __eq__(self, other: DateIntervalParameter):
        return self.start == other.start and self.end == other.end

    def _includes(self, other: DateIntervalParameter):
        return (
            self.start < other.start
            and self.end > other.end
        )

    def is_eq_superset(self, other: DateIntervalParameter):
        return (self == other) or self._includes(other)

    def difference(self, other: DateIntervalParameter) -> DateIntervalParameter:
        if self._includes(other):
            return self
        elif other._includes(self):
            return other
        else:
            if other.start < self.start:
                start = other.start
                end = self.start
            else:
                start = self.end
                end = other.end
            return DateIntervalParameter(start, end)

    def __repr__(self) -> str:
        return f"{self.value_api}"
