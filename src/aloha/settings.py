import os

from .config.hocon import load_config_from_hocon
from .config.paths import get_resource_dir, get_config_dir


class Settings:
    def __init__(self):
        self._config = None

    @property
    def resource_dir(self):
        return get_resource_dir()

    @property
    def config_dir(self):
        return get_config_dir()

    @property
    def config(self):
        if self._config is None:
            # load config items from hocon config files
            _file_config_main = os.path.join(self.config_dir, 'main.conf')
            self._config = load_config_from_hocon(_file_config_main)
        return self._config

    def __getitem__(self, item):
        return self.config[item]


SETTINGS = Settings()
