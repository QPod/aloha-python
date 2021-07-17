__all__ = ('get_resource_dir', 'get_config_dir', 'get_current_module_dir', 'get_project_base_dir')

import os

_pjoin = os.path.join
_env = os.environ


def get_resource_dir():
    dir_cwd = os.getcwd()
    dir_resource = _env.get('DIR_RESOURCE', 'resource')
    return _pjoin(dir_cwd, dir_resource)


def get_config_dir():
    dir_config = _env.get('DIR_CONFIG')
    dir_resource = get_resource_dir()
    if dir_config is None or len(dir_config.strip()) == 0:
        dir_config = 'config'
    dir_config = _pjoin(dir_resource, dir_config)
    print(' ---> Using config dir:', dir_config)
    return dir_config


def get_current_module_dir(file_caller: str):
    dirs = file_caller.split(os.sep)
    return os.sep.join(dirs[:-1])


def get_project_base_dir(file_caller: str):
    dirs = file_caller.split(os.sep)

    dir_base = None
    for i in range(len(dirs)):
        dir_base = os.sep.join(dirs[:-1 - i])
        file_init = _pjoin(dir_base, '__init__.py')
        if not os.path.exists(file_init):
            break
    return dir_base
