"""\
Module to manage constants.

This module defines a Singleton, in this way the file constants.cfg is loaded only once.
The singleton pattern was taken from here
https://refactoring.guru/design-patterns/singleton/python/example#example-0
"""
# pylint: disable=no-else-return
# pylint: disable=missing-function-docstring
from __future__ import annotations


class Singleton(type):
    # pylint: disable=too-few-public-methods
    """This meta class is needed to implement a singleton pattern."""

    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            instance = super().__call__(*args, **kwargs)
            cls._instances[cls] = instance
        return cls._instances[cls]
