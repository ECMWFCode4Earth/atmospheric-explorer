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
import configparser
import operator
import os

import xarray as xr

from .exceptions import OperationNotAllowed
from .loggers import get_logger

logger = get_logger("main")


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

    def arithmetic_eval(self: OperationParser, operation_str: str):
        """Parse an arithmetic operation."""
        logger.debug("Parsing %s", operation_str)
        node = ast.parse(operation_str, mode="eval")

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


class ConstantsMeta(type):
    # pylint: disable=too-few-public-methods
    """\
    This meta class is needed to implement a singleton pattern so that
    constants are loaded only once.
    """
    _instances = {}

    def __init__(cls, *args, **kwargs):
        filepath = os.path.join(
            os.path.dirname(os.path.abspath(__file__)), "constants.cfg"
        )
        cls.constants = configparser.ConfigParser()
        cls.constants.read(filepath)
        logger.info("Loaded constants from file constants.cfg")
        parser = OperationParser()
        # Convert formulas inside configuration to floats
        logger.info("Evaluating arithmetic formulas in config")
        for section in cls.constants.sections():
            cls.constants.set(
                section,
                "factor",
                str(parser.arithmetic_eval(cls.constants[section]["factor"])),
            )
        logger.info("Finished loading constants from file")
        super().__init__(*args, **kwargs)

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            instance = super().__call__(*args, **kwargs)
            cls._instances[cls] = instance
        return cls._instances[cls]


class Constants(metaclass=ConstantsMeta):
    # pylint: disable=too-few-public-methods
    """\
    This class is needed to implement a singleton pattern so that
    constants are loaded only once.
    """

    @classmethod
    def get_constants(cls):
        """Function to get the actual constants object."""
        return cls().constants


def get_constants():
    """Get the actual constants object from the singleton class."""
    return Constants.get_constants()


def convert_units_array(array: xr.DataArray, quantity: str) -> xr.DataArray:
    """\
    Converts an xarray.DataArray from its original units
    to the units specified in the constants.cfg file.
    """
    const = get_constants()
    res = array * const.getfloat(quantity, "factor")
    res.attrs = array.attrs
    res.attrs["units"] = const[quantity]["unit"]
    return res
