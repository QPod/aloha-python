__all__ = ('DuckOperator',)

from pathlib import Path

import duckdb
import duckdb_engine
from aloha.logger import LOG
from sqlalchemy import create_engine, text

LOG.debug('duckdb version = %s, duckdb_engine = %s ' % (duckdb.__version__, duckdb_engine.__version__))


class DuckOperator:
    def __init__(self, db_config, **kwargs):
        """
        db_config example:
        {
            "path": "/path/to/db.duckdb",     # 数据库文件路径，使用 ":memory:" 表示内存模式
            "schema": "sales",                # 可选，默认 'main'
            "read_only": True,                # 可选，默认 False (内存模式下强制为 False)
            "config": {"memory_limit": "500mb"}# 可选，DuckDB 连接配置
        }
        """
        self._config = {
            'path': db_config.get('path', ':memory:'),
            'schema': db_config.get('schema', 'main'),
            'read_only': bool(db_config.get('read_only', False)),
            'config': db_config.get('config', {}),
        }

        if not self._config['path'] or self._config['path'] == ':memory:':  # 标准化内存模式路径
            self._config['path'] = ':memory:'

            if self._config['read_only']:  # 内存数据库不支持只读模式
                LOG.warning("In-memory database cannot be read-only. Setting read_only=False.")
                self._config['read_only'] = False

        else:
            self._prepare_database()

        try:
            str_connection = f"duckdb:///{self._config['path']}"
            self.conn = create_engine(
                str_connection,
                connect_args={
                    'read_only': self._config['read_only'],
                    'config': self._config['config']
                },
                **kwargs
            ).connect()

            self._initialize_schema()

            LOG.debug(
                f"DuckDB connected: {self._config['path']} [schema={self._config['schema']}, read_only={self._config['read_only']}]"
            )
        except Exception as e:
            LOG.exception(e)
            raise RuntimeError('Failed to connect to DuckDB')

    def _prepare_database(self):
        """准备数据库文件和目录"""
        path = self._config['path']
        path_obj = Path(path)

        parent_dir = path_obj.parent
        if not parent_dir.exists():
            if self._config['read_only']:
                raise RuntimeError(
                    f"Directory '{parent_dir}' does not exist and read_only=True"
                )
            try:
                parent_dir.mkdir(parents=True, exist_ok=True)
                LOG.debug(f"Created directory: {parent_dir}")
            except Exception as e:
                raise RuntimeError(f"Failed to create directory '{parent_dir}': {e}")

        if not path_obj.exists():
            if self._config['read_only']:
                raise RuntimeError(
                    f"DuckDB file '{path}' does not exist and read_only=True"
                )
            try:
                LOG.debug(f"Database file not found, creating: {path}")
                duckdb.connect(path).close()
            except Exception as e:
                raise RuntimeError(f"Failed to create database file '{path}': {e}")

    def _initialize_schema(self):
        if self._config['schema'] == 'main':
            return

        try:
            if self._config['read_only']:
                result = self.conn.execute(
                    text("SELECT schema_name FROM information_schema.schemata WHERE schema_name = :schema"),
                    {'schema': self._config['schema']}
                )
                if not result.fetchone():
                    raise RuntimeError(
                        f"Schema '{self._config['schema']}' does not exist and read_only=True"
                    )
            else:
                self.conn.execute(text(f"CREATE SCHEMA IF NOT EXISTS {self._config['schema']}"))

            self.conn.execute(text(f"SET schema '{self._config['schema']}'"))
        except Exception as e:
            raise RuntimeError(f'Failed to initialize schema: {e}')

    @property
    def connection(self):
        return self.conn

    def execute_query(self, sql, auto_commit: bool = True, *args, **kwargs):
        cur = self.conn.execute(text(sql), *args, **kwargs)
        if auto_commit:
            self.conn.commit()
        return cur

    @property
    def connection_str(self) -> str:
        return f"duckdb:///{self._config['path']} [schema={self._config['schema']}, read_only={self._config['read_only']}]"
