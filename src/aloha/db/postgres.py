__all__ = ('PostgresOperator',)

import psycopg2
from sqlalchemy import create_engine
from sqlalchemy.sql import text

from .base import password_vault
from ..logger import LOG

LOG.debug('postgres: psycopg2 version = %s' % psycopg2.__version__)


class PostgresOperator:
    def __init__(self, db_config, **kwargs):
        self._config = {
            'user': db_config['user'],
            'password': password_vault.get_password(db_config.get('password')),
            'host': db_config['host'],
            'port': db_config['port'],
            'dbname': db_config['dbname']
        }
        connect_args = {}
        if 'schema' in db_config:
            connect_args['options'] = '-csearch_path={}'.format(db_config['schema'])

        try:
            self.engine = create_engine(
                'postgresql+psycopg2://{user}:{password}@{host}:{port}/{dbname}'.format(**self._config),
                connect_args=connect_args, client_encoding='utf8', encoding='utf-8',
                pool_size=20, max_overflow=10, pool_pre_ping=True, **kwargs
            )
            LOG.debug("PostgresSQL connected: {host}:{port}/{dbname}".format(**self._config))
        except Exception as e:
            LOG.error(e)
            raise RuntimeError('Failed to connect to PostgresSQL')

    @property
    def connection(self):
        return self.engine

    def execute_query(self, sql, *args, **kwargs):
        with self.engine.connect() as conn:
            cur = conn.execute(text(sql), *args, **kwargs)
            return cur
