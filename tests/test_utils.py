# pylint: disable=missing-module-docstring
# pylint: disable=missing-function-docstring
import os

from atmospheric_explorer.utils import get_local_folder


def test_get_local_folder():
    root_folder = os.getenv("LOCALAPPDATA") or os.getenv("HOME") or "."
    local_folder = get_local_folder()
    assert root_folder in local_folder
