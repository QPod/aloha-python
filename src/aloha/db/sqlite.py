__all__ = ('SqliteOperator',)

import sqlite3

from sqlalchemy import create_engine
from sqlalchemy.sql import text

from .base import PasswordVault
from ..logger import LOG


class SqliteOperator:
    def __init__(self, db_config, **kwargs):
        self._connection_pattern = "sqlite://{dbname}"
        dbname = db_config.get('dbname', '')
        if len(dbname) > 0:
            dbname = '/%s' % dbname
        self._config = {'dbname': dbname}

        if 'password' in db_config:
            try:
                import sqlcipher3
            except ImportError:
                raise RuntimeError('Python package required for encrypted sqlite3: sqlcipher3-binary')
            LOG.debug('Version of sqlcipher3 = %s' % sqlcipher3.sqlite_version)
            password_vault = PasswordVault.get_vault(db_config.get('vault_type'), db_config.get('vault_config'))
            password = password_vault.get_password(db_config.get('password', None))
            self._config['password'] = password
            self._connection_pattern = "sqlite+pysqlcipher://:{password}@/{dbname}"
        else:
            LOG.debug('Version of sqlite = %s' % sqlite3.sqlite_version)

        try:
            self.db = create_engine(
                self._connection_pattern.format(**self._config), **kwargs
            )
            LOG.debug("Sqlite connected: %s" % self.connection_str)
        except Exception as e:
            LOG.exception(e)
            raise RuntimeError('Failed to connect to sqlite')

    @property
    def connection(self):
        return self.db

    def execute_query(self, sql, *args, **kwargs):
        with self.db.connect() as conn:
            cur = conn.execute(text(sql), *args, **kwargs)
            return cur

    @property
    def connection_str(self) -> str:
        return self._connection_pattern.format(**self._config)
