import redis
from rediscluster import StrictRedisCluster

from .base import password_vault
from ..logger import LOG


def get_redis_connection(config):
    try:
        return get_redis_cluster_connection(config)
    except Exception as e:
        return get_redis_default_connection(config)


def get_redis_default_connection(config):
    _config = {
        'host': config.get('host'),
        'port': config.get('port', '1251'),
        'password': password_vault.get_password(config.get('password', None)),
        'db': config.get('db_select', 0),
        'max_connections': config.get('max_connections', 1000)
    }
    LOG.debug("Redis connection info: " + str(_config['host']))
    pool = redis.ConnectionPool(**_config)
    conn = redis.Redis(connection_pool=pool)
    return conn


def get_redis_cluster_connection(config):
    host = config.get('host')
    port = config.get('port', '1251')
    password = config.get('password', None)
    startup_nodes = [{"host": host, "port": port}]

    _config = {
        'startup_nodes': startup_nodes,
        'retry_on_timeout': True,
        'max_connections': config.get('max_connections', 1000),
        'max_connections_per_node': True,
        'socket_timeout': 3,
        'socket_connect_timeout': 1,
        'password': password_vault.get_password(password)
    }
    LOG.debug("StrictRedisCluster connection info: " + str(_config['host']))
    return StrictRedisCluster(**_config)
