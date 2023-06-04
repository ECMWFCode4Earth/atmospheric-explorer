"""\
Module to manage logging.
"""
import logging
import logging.config
import os

_logfile_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "logging.ini")
logging.config.fileConfig(_logfile_path)
# pylint: disable=unused-argument
# ruff: noqa: F401
_main_logger = logging.getLogger("main")