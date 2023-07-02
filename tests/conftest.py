"""\
Config and global variables used in tests
"""
# pylint: disable=missing-module-docstring
# pylint: disable=missing-class-docstring
# pylint: disable=missing-function-docstring
# pylint: disable=protected-access
# pylint: disable=unused-argument
from __future__ import annotations

import pytest
import requests.exceptions

from atmospheric_explorer.cams_interfaces import CAMSDataInterface


class CAMSDataInterfaceTesting(CAMSDataInterface):
    """Mock class used to instantiate CAMSDataInterface so that it can be tested"""

    def includes(self: CAMSDataInterfaceTesting, other: CAMSDataInterfaceTesting):
        """Mock function needed to instantiate CAMSDataInterface"""
        return True

    def read_dataset(self: CAMSDataInterface):
        pass

@pytest.fixture
def mock_get_timeout(monkeypatch):
    def mock_get(*args, **kwargs):
        raise requests.exceptions.Timeout()

    monkeypatch.setattr(requests, "get", mock_get)
