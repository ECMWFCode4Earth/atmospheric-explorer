from __future__ import annotations

from dataclasses import dataclass, field
from itertools import product
from typing import Generator, get_type_hints, Union, Any, get_origin, reveal_type
from types import UnionType
from collections.abc import Iterable

from atmospheric_explorer.loggers import get_logger
from abc import ABC, abstractmethod

logger = get_logger("atmexp")


class CAMSParameters:
    def __init__(self, cls):
        self.cls = cls
        self._point_params = []
        self._set_params = []
        self._interval_params = []

    @staticmethod
    def _convert_to_set(val: str | set[str] | list[str], type_var: type = str):
        if isinstance(val, str):
            val = [val]
        return set([type_var(y) for y in val])


    @abstractmethod
    def build_call_body(self: CAMSParameters):
        raise NotImplementedError("Method not implemented")

@dataclass
class EAC4Parameters(CAMSParameters):
    file_format: set[str]
    data_variables: str | set[str] | list[str]
    dates_range: str
    time_values: str | set[str] | list[str]

    def build_call_body(self: CAMSParameters):
        pass



if __name__ == "__main__":
    p1 = EAC4Parameters(
        file_format=["a"],
        data_variables=["b", "c"],
        dates_range="c",
        time_values=["00:00", "03:00"]
    )
    print({
        k: get_origin(v) for k,v in get_type_hints(p1).items()
    })
    print({
        k: issubclass(get_origin(v), Iterable) for k,v in get_type_hints(p1).items()
    })
