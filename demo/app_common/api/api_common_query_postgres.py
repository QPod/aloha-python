from typing import Optional

import pandas as pd
from sqlalchemy import text

from aloha.base import BaseModule
from aloha.db.postgres import PostgresOperator
from aloha.logger import LOG
from aloha.service.api.v0 import APIHandler


class ApiQueryPostgres(APIHandler):
    def response(self, sql: str, orient: str = 'columns', config_profile: str = None,
                 params=None, *args, **kwargs) -> str:
        op_query_db = QueryDb()
        df = op_query_db.query_db(sql=sql, config_profile=config_profile, params=params)
        ret = df.to_json(orient=orient, force_ascii=False)
        return ret


class QueryDb(BaseModule):
    """Read Data"""

    def get_operator(self, config_profile: str, *args, **kwargs):
        config_dict = self.config[config_profile]
        return PostgresOperator(config_dict)

    def query_db(self, sql: str, config_profile: str = None, params=None, *args, **kwargs) -> Optional[pd.DataFrame]:
        op = self.get_operator(config_profile or 'pg_rec_readonly')
        return pd.read_sql(sql=text(sql), con=op.engine, params=params)


default_handlers = [
    # internal API: QueryDB Postgres with sql directly
    (r"/api_internal/query_postgres", ApiQueryPostgres),
]


def main():
    import sys
    import argparse
    sys.argv.pop(0)
    parser = argparse.ArgumentParser()
    parser.add_argument("--config-profile")
    parser.add_argument("--sql", nargs='?')
    args = parser.parse_args()
    dict_params = vars(args)

    query = QueryDb()
    op = query.get_operator(**dict_params)
    LOG.info('Connection string: %s' % op.connection_str)

    if dict_params.get('sql', None) is not None:
        from tabulate import tabulate
        LOG.info('Query result for: %s' % dict_params['sql'])
        df = query.query_db(**dict_params)
        table = tabulate(df, headers='keys', tablefmt='psql')
        print(table)
