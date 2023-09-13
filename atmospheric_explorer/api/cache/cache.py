"""This module defines classes used for caching."""
from __future__ import annotations

from abc import ABC, abstractmethod
from functools import wraps
from textwrap import dedent

from atmospheric_explorer.api.loggers import get_logger

logger = get_logger("atmexp")


class Parameters(ABC):
    """Abstract class to instantiate a dataset parameter used for caching."""

    @abstractmethod
    def subset(self, parameters: Parameters) -> bool:
        """Determine wether this parameters instance makes up a subset of parameters."""
        raise NotImplementedError(
            "A parameters class needs to implement the subset method"
        )


class Cached:
    """This class defines a few methods that allow to cache another class instances.
    Caching is based on the class attributes.

    To cache a class, inherit from this class and define the subset method,
    which is used inside find_cache to determine wether an instance is already included
    or is equal to another instance. Last, one needs to decorate the new class __init__ with the
    static method Cached.init_cache.
    """

    _cache: list[Cached] = []

    @classmethod
    def find_cache(cls: Cached, parameters: Parameters) -> Cached | None:
        """Find obj in cache that has a superset of the parameters passed in kwargs."""
        logger.debug("Looking in cache for parameters %s", parameters)
        for sd_obj in cls._cache:
            if isinstance(sd_obj.parameters, type(parameters)) and parameters.subset(
                sd_obj.parameters
            ):
                logger.debug("Found cached object %s", sd_obj)
                return sd_obj
        logger.debug("Object with parameters %s is not cached", parameters)
        return None

    def is_cached(self) -> bool:
        """Check if self or a superset of it is already cached."""
        return self in type(self)._cache

    def cache(self) -> None:
        """Cache self."""
        logger.debug("Caching object %s", self)
        type(self)._cache.append(self)

    @classmethod
    def clear_cache(cls):
        """Clear cache."""
        logger.debug("Cleared objects %s from cache", cls)
        cls._cache = list(filter(lambda obj: not(isinstance(obj,cls)), cls._cache))

    def __new__(cls: Cached, parameters: Parameters):
        logger.debug(
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
        logger.debug("Cached object not found, creating a new one")
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
            logger.debug("Initializing an instance of %s", type(self))
            func(self, *args, **kwargs)
            self.cache()

        return wrapper
