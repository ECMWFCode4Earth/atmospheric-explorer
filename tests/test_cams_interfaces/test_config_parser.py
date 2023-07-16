# pylint: disable=missing-module-docstring
# pylint: disable=missing-class-docstring
# pylint: disable=missing-function-docstring
# pylint: disable=protected-access
# pylint: disable=unused-argument
import pytest

from atmospheric_explorer.cams_interface.config_parser import OperationParser
from atmospheric_explorer.exceptions import OperationNotAllowed


def test_arithmetic_eval():
    parser = OperationParser()
    assert parser.arithmetic_eval("1+1") == 2
    assert parser.arithmetic_eval("1-1") == 0
    assert parser.arithmetic_eval("1/2") == 0.5
    assert parser.arithmetic_eval("2*2.5") == 5
    assert parser.arithmetic_eval("15%11") == 4


def test_arithmetic_unsupported():
    with pytest.raises(OperationNotAllowed):
        parser = OperationParser()
        parser.arithmetic_eval("2**2")
