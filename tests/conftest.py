"""\
Config and global variables used in tests
"""
from __future__ import annotations

from atmospheric_explorer.cams_interfaces import CAMSDataInterface


class CAMSDataInterfaceTesting(CAMSDataInterface):
    """Mock class used to instantiate CAMSDataInterface so that it can be tested"""

    def is_included(self: CAMSDataInterfaceTesting, other: CAMSDataInterfaceTesting):
        """Mock function needed to instantiate CAMSDataInterface"""
        return True
