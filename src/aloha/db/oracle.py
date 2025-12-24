__all__ = ('OracledbOperator',)

import oracledb
from sqlalchemy import create_engine
from sqlalchemy.sql import text


from .base import PasswordVault
from ..logger import LOG

LOG.debug('Version of oracledb = %s' % oracledb.__version__)


class OracledbOperator:
    def __init__(self, db_config, **kwargs):
        """example of db_config:
        {
            "host": "192.168.1.100",
            "port": 1521,
            "user": "PT_INDEX",
            "password": "vault_key_or_plain",
            "service_name": "orcl",   # 推荐使用 service_name
            "sid": "orcl",            # 或使用 sid
            "vault_type": "...",
            "vault_config": {...},
            "lib_dir": "/opt/oracle/instantclient"  # optional, use THICK mode if defined.
        }
        """

        self._config = {
            'host': db_config['host'],
            'port': db_config['port'],
            'user': db_config['user'],
            'password': db_config['password'],
        }

        if 'lib_dir' in db_config:  # use Thick mode
            try:
                oracledb.init_oracle_client(lib_dir=db_config['lib_dir'])
                print("Oracle client initialized in THICK mode from: %s" % db_config['lib_dir'])
            except Exception as e:
                print(f"Warning: {e}")
                raise RuntimeError(f"Failed to initialize Oracle client: {e}")

            print("is_thin =", oracledb.is_thin_mode())

        service_name = db_config.get("service_name")
        sid = db_config.get("sid")

        if service_name:  # using service_name (recommended)
            dsn = oracledb.makedsn(db_config['host'],  db_config['port'],  service_name=service_name)
        elif sid:  # using SID
            dsn = oracledb.makedsn(db_config['host'], db_config['port'], sid=sid)
        else:
            raise ValueError("Oracle config must specify service_name or sid")

        self._config["dsn"] = dsn
        try:
            self.engine = create_engine(
                "oracle+oracledb://{user}:{password}@".format(**self._config),
                connect_args={"dsn": dsn},
                pool_size=20,
                max_overflow=10,
                pool_pre_ping=True,
                **kwargs
            )
            msg = "OracleDB connected: {host}:{port}".format(**self._config)
            print(msg)
        except Exception as e:
            raise RuntimeError(f"Failed to connect to OracleDB: {e}")

    @property
    def connection(self):
        return self.engine

    def execute_query(self, sql, *args, **kwargs):
        """returns SQLAlchemy CursorResult"""
        with self.engine.connect() as conn:
            cur = conn.execute(text(sql), *args, **kwargs)
            return cur

    @property
    def connection_str(self) -> str:
        return "oracle://{user}@{host}:{port}".format(**self._config)
