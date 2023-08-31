# pylint: disable=missing-module-docstring
# pylint: disable=missing-class-docstring
# pylint: disable=missing-function-docstring
# pylint: disable=protected-access
# pylint: disable=unused-argument
import os

from atmospheric_explorer.os_manager import get_local_folder


def test_get_local_folder():
    root_folder = os.getenv("LOCALAPPDATA") or os.getenv("HOME") or "."
    local_folder = get_local_folder()
    assert root_folder in local_folder
