import unittest
from abc import ABC

from ..logger import LOG
from ..settings import SETTINGS


class UnitTestCase(unittest.TestCase, ABC):
    LOG = LOG
    config = SETTINGS.config
