__all__ = ('DuckOperator',)

import duckdb
from sqlalchemy import create_engine
from sqlalchemy.sql import text

from ..logger import LOG

LOG.debug('duckdb: duckdb version = %s' % duckdb.__version__)


class DuckOperator:
    def __init__(self, db_config, **kwargs):
        self._config = {
            'path': db_config['path'],
            'dbname': db_config['dbname'],
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

    @property
    def connection_str(self) -> str:
        return "duckdb:///{user}:{password}@{host}:{port}/{dbname}".format(**self._config)
