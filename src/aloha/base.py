from abc import ABC

from .logger import LOG
from .settings import SETTINGS


class BaseModule(ABC):
    config = SETTINGS.config
    LOG = LOG
