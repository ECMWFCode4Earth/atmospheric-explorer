# pylint: disable=missing-module-docstring
# pylint: disable=missing-class-docstring
# pylint: disable=missing-function-docstring
# pylint: disable=protected-access
# pylint: disable=unused-argument
from __future__ import annotations

import pytest

from atmospheric_explorer.api.cache.cache import Cached, Parameters


class ParametersClass(Parameters):
    def __init__(self: ParametersClass, arg):
        self.arg = arg

    def subset(self: ParametersClass, other: ParametersClass) -> bool:
        return self.arg == other.arg


class CachedClass(Cached):

    def __new__(cls, arg):
        par = ParametersClass(arg)
        return Cached.__new__(CachedClass, par)

    @Cached.init_cache
    def __init__(self, arg):
        self.parameters = ParametersClass(arg)


@pytest.fixture(autouse=True)
def clear_cache():
    CachedClass.clear_cache()
    yield
    CachedClass.clear_cache()


def test_cache():
    assert not CachedClass._cache
    sh1 = CachedClass.__new__(CachedClass, arg="1")
    sh2 = CachedClass.__new__(CachedClass, arg="2")
    sh1.cache()
    sh2.cache()
    assert len(CachedClass._cache) == 2
    assert CachedClass._cache[0] is sh1
    assert CachedClass._cache[1] is sh2


def test_find_cache():
    sh1 = CachedClass(arg="1")
    assert CachedClass.find_cache(ParametersClass(arg="1")) is sh1
    assert CachedClass.find_cache(ParametersClass(arg="2")) is None


def test_is_cached():
    sh1 = CachedClass(arg="1")
    assert sh1.is_cached()
    sh2 = CachedClass.__new__(CachedClass, arg="2")
    assert not sh2.is_cached()


def test_clear_cache():
    CachedClass(arg="1")
    assert CachedClass._cache
    CachedClass.clear_cache()
    assert not CachedClass._cache


def test_obj_creation():
    sh1 = CachedClass(arg="1")
    sh2 = CachedClass(arg="1")
    assert id(sh1) == id(sh2)
    assert sh1 in CachedClass._cache
    sh3 = CachedClass(arg="3")
    assert id(sh3) != id(sh1)
