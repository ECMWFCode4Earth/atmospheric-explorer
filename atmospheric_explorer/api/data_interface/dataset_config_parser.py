"""Module to manage constants.

This module defines a Singleton, in this way the file constants.cfg is loaded only once.
The singleton pattern was taken from here
https://refactoring.guru/design-patterns/singleton/python/example#example-0
"""
# pylint: disable=no-else-return
# pylint: disable=missing-function-docstring
from __future__ import annotations

import ast
import operator
import os
from functools import singledispatchmethod

import yaml

from atmospheric_explorer.api.exceptions import OperationNotAllowed
from atmospheric_explorer.api.loggers.loggers import atm_exp_logger


class OperationParser:
    # pylint: disable=too-few-public-methods
    """Parser for arithmetic operations.

    Code for this class was taken from
    https://stackoverflow.com/questions/20748202/valueerror-malformed-string-when-using-ast-literal-eval
    """

    allowed_ops = {
        ast.Add: operator.add,
        ast.Sub: operator.sub,
        ast.Mult: operator.mul,
        ast.Div: operator.truediv,
        ast.Mod: operator.mod,
    }

    @singledispatchmethod
    def arithmetic_eval(self, operation: str) -> str:
        """Parse an arithmetic operation passed as a string."""
        node = ast.parse(operation, mode="eval")

        def _eval(node):
            if isinstance(node, ast.Expression):
                return _eval(node.body)
            elif isinstance(node, ast.Str):
                return node.s
            elif isinstance(node, ast.Num):
                return node.n
            elif isinstance(node, ast.BinOp):
                try:
                    return self.allowed_ops[type(node.op)](
                        _eval(node.left), _eval(node.right)
                    )
                except KeyError as exc:
                    atm_exp_logger.error(exc)
                    atm_exp_logger.error("Unsupported operation %s", type(node.op))
                    raise OperationNotAllowed(
                        f"Unsupported operation {type(node.op)}"
                    ) from exc
            else:
                atm_exp_logger.error("Unsupported type %s", node)
                raise OperationNotAllowed(f"Unsupported type {node}")

        return _eval(node.body)

    @arithmetic_eval.register(int)
    @arithmetic_eval.register(float)
    def _(self, operation: int | float) -> int | float:
        """Parse a number, i.e. returns it unchanged."""
        return operation

    @arithmetic_eval.register
    def _(self, operation: list) -> list:
        """Parse a list of operations."""
        return [self.arithmetic_eval(op) for op in operation]


class DatasetConfigParser:
    # pylint: disable=too-few-public-methods
    """This class implements some basic functionalities to parse a YAML file containing the configuration for a dataset,
    i.e. variables, conversion factors etc.

    For reference, check the file atmospheric_explorer/api/data_interface/ghg/ghg_config.yaml.

    A dataset configuration file is **expected** to have data structured in the following way

    variables:
        data_variable_name:
            var_name: # name of the dataset column
            conversion:
                conversion_factor: ...
                conversion_unit: ...
    """

    _parser = OperationParser()

    def __init__(self, **kwargs):
        filename = kwargs["filename"]
        filepath = os.path.join(os.path.dirname(os.path.abspath(__file__)), filename)
        with open(filepath, "r", encoding="utf-8") as file:
            atm_exp_logger.debug("Reading config from file %s", file.name)
            self.config = yaml.safe_load(file)
        # Convert formulas inside configuration to floats
        atm_exp_logger.debug("Evaluating arithmetic formulas in config")
        self.parse_factors(self.config["variables"])

    @classmethod
    def get_config(cls) -> dict:
        """Function to get the actual config object."""
        return cls().config

    @singledispatchmethod
    @classmethod
    def parse_factors(cls, data_dict: dict):
        """Parse conversion factors in a dataset config file.
        
        The file is **expected** to have a 'conversion' section.
        """
        if data_dict.get("conversion") is not None:
            data_dict["conversion"]["conversion_factor"] = cls._parser.arithmetic_eval(
                data_dict["conversion"]["conversion_factor"]
            )
        else:
            for k in data_dict.keys():
                cls.parse_factors(data_dict[k])

    @parse_factors.register
    @classmethod
    def _(cls, data: list):
        for elem in data:
            cls.parse_factors(elem)
