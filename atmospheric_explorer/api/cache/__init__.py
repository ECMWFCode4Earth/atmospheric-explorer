"""Module containing all caching functionalities for CAMS datasets.

Datasets are downloaded when needed, and each call is cached **in memory** in order to avoid
downloading the same dataset multiple times.

In this submodule we define two classes:

- Parameters:
    Abstract base class to be inherited by the dataset parameters.

    Each dataset should have a Parameters subclass where all its cdsapi parameters are defined.

    This class also expects a `subset` instance method to be defined:
    this method expects another Parameters instance as the `other` argument
    and returns True if `other` has the same or a superset of the Parameters
    of the `self` instance.

- Cached:
    Class with some methods needed for caching a CAMS dataset call.

    To cache a class, inherit from this class and define the `__new__` method:
    this method is only needed to instantiate the Parameters instance
    corresponding to the specific CAMS dataset and pass it to Cached.__new__.

    Last, one needs to decorate the new class __init__ with the static method Cached.init_cache.

    See eac4 and ghg submodules as an example.

Note that this cache only keeps track of files downloaded during a session and ignores preiously downloaded files.
This means that it only works when using the UI or the APIs,
while doesn't work with the CLI since each command is a session by itself.
"""
# pylint: disable=missing-module-docstring
# ruff: noqa: F401
from atmospheric_explorer.api.cache.cache import Cached, Parameters
