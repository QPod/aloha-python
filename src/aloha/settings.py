from .config import hocon, paths


class Settings:
    def __init__(self):
        self._config = None

    @property
    def resource_dir(self):
        return paths.get_resource_dir()

    @property
    def config_dir(self):
        return paths.get_config_dir()

    @property
    def config(self):
        if self._config is None:
            config_files = paths.get_config_files()  # by default, use the `main.conf` file in the config_dir
            self._config = hocon.load_config_from_hocon_files(config_files, base_dir=paths.get_config_dir())

        return self._config

    def __getitem__(self, item):
        return self.config[item]


SETTINGS = Settings()
