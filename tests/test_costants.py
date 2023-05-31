# pylint: disable=missing-module-docstring
# pylint: disable=missing-function-docstring
from atmospheric_explorer.constants import get_constants


def test_singleton():
    object_first = get_constants()
    object_second = get_constants()
    assert id(object_first) == id(object_second)
