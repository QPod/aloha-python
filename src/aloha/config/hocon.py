from attrdict import AttrDict
from pyhocon import ConfigFactory


def load_config_from_hocon(config_file):
    config = ConfigFactory.parse_file(config_file).as_plain_ordered_dict()
    return config


def load_config_from_hocon_files(config_files: list, base_dir: str):
    s = []
    for config_file in config_files:
        f = 'include required("%s")' % config_file
        s.append(f)
    f = '\n'.join(s)

    config = ConfigFactory.parse_string(content=f, basedir=base_dir).as_plain_ordered_dict()
    return AttrDict(config)
