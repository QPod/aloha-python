from pyhocon import ConfigFactory


def load_config_from_hocon(config_file):
    config = ConfigFactory.parse_file(config_file).as_plain_ordered_dict()
    return config
