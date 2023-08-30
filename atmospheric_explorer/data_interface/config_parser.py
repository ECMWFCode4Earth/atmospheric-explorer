"""\
Module to manage constants.
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

from ..exceptions import OperationNotAllowed
from ..loggers import get_logger

logger = get_logger("atmexp")


class OperationParser:
    """\
    Parser for arithmetic operations. Code for this class was taken
    from https://stackoverflow.com/questions/20748202/valueerror-malformed-string-when-using-ast-literal-eval
    """

    # pylint: disable=too-few-public-methods

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
                    logger.error(exc)
                    logger.error("Unsupported operation %s", type(node.op))
                    raise OperationNotAllowed(
                        f"Unsupported operation {type(node.op)}"
                    ) from exc
            else:
                logger.error("Unsupported type %s", node)
                raise OperationNotAllowed(f"Unsupported type {node}")

        return _eval(node.body)

    @arithmetic_eval.register
    def _(self, operation: int | float) -> int | float:
        """Parse a number, i.e. returns it unchanged."""
        return operation

    @arithmetic_eval.register
    def _(self, operation: list) -> list:
        """Parse a list of operations."""
        return [self.arithmetic_eval(op) for op in operation]


class ConfigMeta(type):
    """\
    This meta class is needed to implement a singleton pattern so that
    the config files are loaded only once.
    """

    # pylint: disable=too-few-public-methods
    _instances = {}
    _parser = OperationParser()

    def __new__(mcs, *args, **kwargs):
        return super().__new__(mcs, *args)

    def __init__(cls, *args, **kwargs):
        filename = kwargs["filename"]
        filepath = os.path.join(os.path.dirname(os.path.abspath(__file__)), filename)
        with open(filepath, "r", encoding="utf-8") as file:
            cls.config = yaml.safe_load(file)
        logger.info("Loaded config from file %s", filename)
        # Convert formulas inside configuration to floats
        logger.info("Evaluating arithmetic formulas in config")
        cls._parse_factors(cls.config["variables"])
        logger.info("Finished loading config from file")
        super().__init__(*args, **kwargs)

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            instance = super().__call__(*args, **kwargs)
            cls._instances[cls] = instance
        return cls._instances[cls]

    @singledispatchmethod
    @classmethod
    def _parse_factors(mcs, data_dict: dict):
        if data_dict.get("conversion") is not None:
            data_dict["conversion"]["conversion_factor"] = mcs._parser.arithmetic_eval(
                data_dict["conversion"]["conversion_factor"]
            )
        else:
            for k in data_dict.keys():
                mcs._parse_factors(data_dict[k])

    @_parse_factors.register
    @classmethod
    def _(mcs, data: list):
        for elem in data:
            mcs._parse_factors(elem)
