import psycopg2

from .base import password_vault
from ..logger import LOG

from sqlalchemy import create_engine
from sqlalchemy.sql import text

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
        LOG.debug("PostgreSQL connection info: " + str(self._config['host']))

        try:
            self.engine = create_engine(
                'postgresql+psycopg2://{user}:{password}@{host}:{port}/{dbname}'.format(**self._config),
                client_encoding='utf8', encoding='utf-8', pool_size=20, max_overflow=0, **kwargs
            )
        except Exception as e:
            LOG.exception(e)
            raise RuntimeError('Failed to connect to PostgresSQL')

    @property
    def connection(self):
        return self.engine

    def execute_query(self, sql, *args, **kwargs):
        with self.engine.connect() as conn:
            cur = conn.execute(text(sql), *args, **kwargs)
            result = cur.fetchall()
            return result
