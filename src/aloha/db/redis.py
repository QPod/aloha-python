__all__ = ('RedisOperator',)

import redis
from packaging import version

from .base import PasswordVault
from ..logger import LOG


class RedisOperator:
    def __init__(self, config):
        self._check_redis_version()

        password_vault = PasswordVault.get_vault(config.get('vault_type'), config.get('vault_config'))
        _config = {
            'host': config['host'],
            'port': config.get('port', '6379'),
            'password': password_vault.get_password(config.get('password', None)),
            'decode_responses': config.get('decode_responses', True),
            'retry_on_timeout': True,
            'max_connections': config.get('max_connections', 1000),
            'socket_timeout': 3,
            'socket_connect_timeout': 1,
        }
        if 'db' in config:
            _config['db'] = config['db']
        self._config = _config

        self._pool = None

    @staticmethod
    def _check_redis_version() -> bool:
        ver_min = version.parse('4.1.0')
        valid = False
        try:
            ver_cur = version.parse(redis.__version__)
            if ver_cur >= ver_min:
                valid = True
                LOG.debug('Using redis version = %s' % redis.__version__)
        except Exception as e:
            LOG.error('Failed to obtain redis version!')
            LOG.error(str(e))

        if not valid:
            msg = 'Invalid version of `redis-py`, version >4.1.0 required!'
            LOG.fatal(msg)
            raise ImportError(msg)

        return valid

    @property
    def connection_generic(self):
        """https://github.com/redis/redis-py/blob/master/redis/client.py"""
        LOG.debug("StrictRedis connection info: {host}:{port}".format(**self._config))

        if self._pool is None:
            self._pool = redis.ConnectionPool()
        return redis.Redis(connection_pool=self._pool, **self._config)

    @property
    def connection_cluster(self):
        LOG.debug("RedisCluster connection info: {host}:{port}".format(**self._config))
        return redis.RedisCluster(**self._config)
