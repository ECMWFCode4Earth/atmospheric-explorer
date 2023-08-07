from __future__ import annotations

from atmospheric_explorer.data_interface.cams_interface.parameters_types import Parameter
from atmospheric_explorer.loggers import get_logger
from pydantic.dataclasses import dataclass as pydantic_dataclass
from abc import ABC, abstractmethod

logger = get_logger("atmexp")


@pydantic_dataclass(kw_only=True)
class CAMSParameters(ABC):

    @abstractmethod
    def build_call_body(self: CAMSParameters) -> dict:
        """Build the CDSAPI call body"""
        raise NotImplementedError()

    @classmethod
    def from_call_body(cls, body: dict):
        for k,v in body.items():
            body[k] = {"value":v}
        return cls(**body)
