"""This module defines classes used for caching."""
from __future__ import annotations

from abc import ABC, abstractmethod
from functools import wraps
from textwrap import dedent

from atmospheric_explorer.api.loggers.loggers import atm_exp_logger


class Parameters(ABC):
    # pylint: disable = too-few-public-methods
    """Abstract class to instantiate dataset parameters, used for caching."""

    @abstractmethod
    def subset(self, other: Parameters) -> bool:
        """Determine wether this parameters instance makes up a subset of parameters."""
        raise NotImplementedError(
            "A Parameters subclass needs to implement the subset method"
        )


class Cached:
    """This class defines a few methods that allow to cache another class instances.

    Caching is based on the class attributes.

    To cache a class, inherit from this class and define the `__new__` method:
    this method is only needed to instantiate the Parameters instance
    corresponding to the specific CAMS dataset and pass it to Cached.__new__.

    Last, one needs to decorate the new class __init__ with the static method Cached.init_cache.
    """

    _cache: list[Cached] = []

    @classmethod
    def find_cache(cls: Cached, parameters: Parameters) -> Cached | None:
        """Find obj in cache that has a superset of the parameters passed in kwargs."""
        atm_exp_logger.debug("Looking in cache for parameters %s", parameters)
        for sd_obj in cls._cache:
            if isinstance(sd_obj.parameters, type(parameters)) and parameters.subset(
                sd_obj.parameters
            ):
                atm_exp_logger.debug("Found cached object %s", sd_obj)
                return sd_obj
        atm_exp_logger.debug("Object with parameters %s is not cached", parameters)
        return None

    def is_cached(self) -> bool:
        """Check if self or a superset of it is already cached."""
        return self in type(self)._cache

    def cache(self) -> None:
        """Cache self."""
        atm_exp_logger.debug("Caching object %s", self)
        type(self)._cache.append(self)

    @classmethod
    def clear_cache(cls):
        """Clear cache."""
        atm_exp_logger.debug("Cleared objects %s from cache", cls)
        cls._cache = list(filter(lambda obj: not (isinstance(obj, cls)), cls._cache))

    def __new__(cls: Cached, parameters: Parameters):
        """Create a new instance of the cached class if there's no similar instance in the cache.

        When attempting to create an instance, a cached class first instantiates its parameters and
        then checks them against other cached instances. If an instance with the same or a superset of parameters
        is found, that instance instead of a new one is returned.
        """
        atm_exp_logger.debug(
            dedent(
                """\
                Attempting to create Cached object with attributes
                %s
                """
            ),
            parameters,
        )
        cached_obj = cls.find_cache(parameters)
        if cached_obj is not None:
            return cached_obj
        atm_exp_logger.debug("Cached object not found, creating a new one")
        return super().__new__(cls)

    @staticmethod
    def init_cache(func):
        """Wrapper for the __init__ method of a cached class.

        Checks if self is already cached. If yes, returs None.
        If not, runs the __init__ and then caches the initialized instance of the class.
        """

        @wraps(func)
        def wrapper(self, *args, **kwargs):
            if self.is_cached():
                return
            atm_exp_logger.debug("Initializing an instance of %s", type(self))
            func(self, *args, **kwargs)
            self.cache()

        return wrapper
