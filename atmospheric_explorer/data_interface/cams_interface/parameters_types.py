from __future__ import annotations

from atmospheric_explorer.loggers import get_logger
from pydantic.dataclasses import dataclass as pydantic_dataclass
from pydantic import computed_field, field_validator, model_validator
from typing import Any
from datetime import datetime
import shapely
import math
from pandas import date_range

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
    format_str: str = None
    _base_type: type = str

    @field_validator('value', mode="before")
    def convert_input(cls, val):
        if not (isinstance(val, list) or isinstance(val, set)):
            val = [val]
        return {cls._base_type(v) for v in val}

    @computed_field
    @property
    def value_api(self) -> list[str]:
        if self.format_str is not None:
            return sorted([f"{v:{self.format_str}}" for v in self.value])
        return sorted([str(v) for v in self.value])

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
    
    def merge(self, other: SetParameter) -> SetParameter:
        val = self.value
        val.update(other.value)
        format_str = self.format_str or other.format_str
        if format_str is None:
            return SetParameter(value=val)
        return SetParameter(value=val, format_str=format_str)


@pydantic_dataclass
class IntSetParameter(SetParameter):
    _base_type: type = int

    def __repr__(self) -> str:
        return f"{self.value_api}"


@pydantic_dataclass
class BoxParameter:
    north: int
    west: int
    south: int
    east: int

    @model_validator(mode='before')
    @classmethod
    def modify_input(cls, data: Any) -> Any:
        kwargs = data.kwargs
        if kwargs is None:
            data = data.args[0]
            data = {
                "north": data[0],
                "west": data[1],
                "south": data[2],
                "east": data[3]
            }
        return data

    @model_validator(mode='after')
    def check_bounds(self) -> DateIntervalParameter:
        if self.north < self.south:
            raise ValueError("North is lower than south!")
        if self.west < self.east:
            raise ValueError("West is lower than east!")
        return self

    @computed_field
    @property
    def value_api(self) -> list[str]:
        return [self.north, self.west, self.south, self.east]

    def _as_shape(self) -> shapely.Polygon:
        return shapely.box(self.east, self.south, self.west, self.north)

    def __eq__(self, other: BoxParameter):
        return (
            self.north == other.north
            and self.south == other.south
            and self.east == other.east
            and self.west == other.west
        )

    def is_eq_superset(self, other: BoxParameter):
        return (self == other) or (
            self.north >= other.north
            and self.south <= other.south
            and self.east <= other.east
            and self.west >= other.west
        )

    @staticmethod
    def is_rect(shape: shapely.Polygon) -> bool:
        return math.isclose(shape.area, shape.minimum_rotated_rectangle.area)

    def difference(self, other: BoxParameter) -> BoxParameter | None:
        s1 = self._as_shape()
        s2 = other._as_shape()
        s_diff = s1 - s2
        if self.is_rect(s_diff):
            bounds = s_diff.bounds
            return BoxParameter(east=bounds[0], south=bounds[1], west=bounds[2], north=bounds[3])
        else:
            return self

    def __repr__(self) -> str:
        return f"{self.value_api}"

    def __iter__(self):
        return iter(self.value_api)
    
    def merge(self, other: BoxParameter) -> BoxParameter:
        north = max(self.north, other.north)
        south = min(self.south, other.south)
        west = max(self.west, other.west)
        east = min(self.east, other.east)
        return BoxParameter(north=north, south=south, east=east, west=west)

@pydantic_dataclass
class DateIntervalParameter:
    start: datetime
    end: datetime
    
    @model_validator(mode='before')
    @classmethod
    def modify_input(cls, data: Any) -> Any:
        kwargs = data.kwargs
        if kwargs is None:
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
    
    @computed_field
    @property
    def all_days(self) -> list[str]:
        return date_range(self.start, self.end, freq='D')

    def __eq__(self, other: DateIntervalParameter):
        return self.start == other.start and self.end == other.end

    def _includes(self, other: DateIntervalParameter):
        return (
            self.start <= other.start
            and self.end >= other.end
        )

    def is_eq_superset(self, other: DateIntervalParameter):
        return (self == other) or self._includes(other)

    def difference(self, other: DateIntervalParameter) -> DateIntervalParameter | None:
        if self.start > other.end:
            start = self.start
            end = self.end
        else:
            if self.end > other.end:
                end = self.end
            else:
                end = other.start
            if self.start < other.start:
                start = self.start
            else:
                start = other.end
        return DateIntervalParameter(start=start, end=end)

    def __repr__(self) -> str:
        return f"{self.value_api}"

    def merge(self, other: DateIntervalParameter) -> DateIntervalParameter:
        start = min(self.start, other.start)
        end = max(self.end, other.end)
        return DateIntervalParameter(start=start, end=end)

if __name__ == '__main__':
    y = IntSetParameter(["1", "2", "3"])
    print(y)
    