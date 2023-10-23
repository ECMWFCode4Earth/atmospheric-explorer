# pylint: disable=missing-module-docstring
# pylint: disable=missing-class-docstring
# pylint: disable=missing-function-docstring
# pylint: disable=protected-access
# pylint: disable=unused-argument
# pylint: disable=too-few-public-methods
from atmospheric_explorer.api.singleton import Singleton


class SingletonConcrete(metaclass=Singleton):
    pass


def test_singleton():
    obj1 = SingletonConcrete()
    obj2 = SingletonConcrete()
    assert id(obj1) == id(obj2)
