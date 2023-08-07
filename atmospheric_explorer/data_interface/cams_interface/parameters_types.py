from __future__ import annotations

from atmospheric_explorer.loggers import get_logger
from pydantic.dataclasses import dataclass as pydantic_dataclass
from pydantic import computed_field, field_validator, model_validator
from typing import Any
from datetime import datetime, timedelta
from pandas import date_range
from itertools import pairwise, groupby, accumulate

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
    
    @classmethod
    def from_dates(cls, dates: list[datetime]) -> DateIntervalParameter | list[DateIntervalParameter]:
        dates = sorted(dates)
        diffs = [0] + [(y-x).days > 1 for x,y in pairwise(dates)]
        diffs_groups = list(accumulate(diffs))
        dates_groups = [[c for _, c in g] for _, g in groupby(zip(diffs_groups, dates), key=lambda x: x[0])]
        dates_ranges = [(min(g), max(g)) for g in dates_groups]
        return [cls(start=r[0], end=r[1]) for r in dates_ranges] if len(dates_ranges) > 1 else cls(start=dates_ranges[0][0], end=dates_ranges[0][1])



if __name__ == '__main__':
    d = DateIntervalParameter.from_dates([datetime(2020, 1, 1), datetime(2020, 1, 2), datetime(2020, 1, 3), datetime(2021, 1, 3), datetime(2021, 1, 4)])
    print(d)