from __future__ import annotations

from pydantic.main import TupleGenerator

from atmospheric_explorer.data_interface.cams_interface.parameters_types import Parameter, ListParameter
from atmospheric_explorer.loggers import get_logger
from pydantic import BaseModel, model_validator

logger = get_logger("atmexp")


class CAMSParameters(BaseModel):
    file_format: Parameter

    @model_validator(mode='before')
    def _(cls, data):
        if isinstance(data, dict):
            for k, v in data.items():
                if not (isinstance(v, dict) and "value" in v.keys()):
                    data[k] = {"value": v}
        return data

    def _cond_over_params(self, other, param_type, func) -> bool:
        for field_name in self.model_fields:
            field_val = getattr(self, field_name)
            if isinstance(field_val, param_type):
                print(field_name)
                if not func(field_val, getattr(other, field_name)):
                    return False
        return True

    def __iter__(self) -> TupleGenerator:
        return self.model_fields

    def _params_eq(self, other: CAMSParameters) -> bool:
        return self._cond_over_params(other, Parameter, (lambda a,b: a == b))

    def _list_params_eq(self, other: CAMSParameters) -> bool:
        return self._cond_over_params(other, ListParameter, (lambda a,b: a == b))

    def _list_params_eq_superset(self, other: CAMSParameters) -> bool:
        return self._cond_over_params(other, ListParameter, (lambda a,b: a.is_eq_superset(b)))

    def __eq__(self, other: CAMSParameters) -> bool:
        return self._params_eq(other) and self._list_params_eq(other)

    def is_eq_superset(self, other: CAMSParameters) -> bool:
        """True if self is equal or a superset of other."""
        return (self == other) or (
            self._params_eq(other)
            and self._list_params_eq_superset(other)
        )

    def build_call_body(self: CAMSParameters) -> dict:
        """Build the CDSAPI call body"""
        return {
            f:getattr(self, f).value_api for f in self.model_fields
        }

    @classmethod
    def from_call_body(cls, body: dict):
        for k,v in body.items():
            body[k] = {"value":v}
        return cls(**body)

    def _list_difference(self, other) -> dict:
        res = {}
        for field_name in self.model_fields:
            field_val = getattr(self, field_name)
            if isinstance(field_val, ListParameter):
                print(field_name)
                diff = field_val.difference(getattr(other, field_name))
                if diff:
                    res[field_name] = diff
        return res

    def difference(self, other: CAMSParameters) -> CAMSParameters | None:
        """Return a CAMSParameters instance with all non-overlapping parameters."""
        if self._params_eq(other):
            logger.debug(
                "Parameters have the same point variables, moving to compute difference in list parameters"
            )
            diff = self._list_difference(other)
            if diff:
                logger.debug("Parameters have different list variables, returning an inclusive parameter set")
                params = self.build_call_body()
                params.update(diff)
                return type(self).from_call_body(params)
            else:
                logger.debug("Parameters are the same")
                return None
        else:
            logger.debug("Point parameters are different")
            return other


if __name__ == "__main__":
    p1 = CAMSParameters(
        file_format="a"
    )
    p2 = CAMSParameters(
        file_format={"value":"b"}
    )
    print(p1)
    print(p2)
