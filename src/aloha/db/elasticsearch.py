__all__ = ('ElasticSearchOperator',)

import json

from elasticsearch import Elasticsearch

from .base import password_vault
from ..logger import LOG


class ElasticSearchOperator:
    def __init__(self, config, index_config=None):
        self.es_config = config

        username = config.get('username')
        password = password_vault.get_password(config.get('password'))

        self._config = {
            'http_auth': (username, password) if username is not None and password is not None else None,
            'hosts': config.get('host', 'localhost'),

            'timeout': config.get("timeout", 0.1),
            'max_retries': config.get("max_retries", 3),
            'retry_on_timeout': config.get("retry_on_timeout", True)
        }
        LOG.debug("ElasticSearch connection info: " + str(self._config['hosts']))

        self.index_config = index_config
        self.index_name = self.es_config.get('index_name')
        self.index_type = self.es_config.get('index_type')

        self.es = Elasticsearch(**self._config)

        if index_config is not None:
            self.index_config = self._load_config(index_config)

    @staticmethod
    def _load_config(config):
        if type(config) == dict:
            return config

        elif type(config) == str and ".json" in config:
            with open(config, "r", encoding="utf-8") as f:
                config = json.load(f)
            return config

        else:
            raise Exception("Invalid ES config data type")

    def put_mapping(self, index_name=None, index_type=None, index_config=None):
        return self.es.indices.put_mapping(
            index=index_name or self.index_name,
            doc_type=index_type or self.index_type,
            body=index_config["mappings"][index_type or self.index_type]
        )

    def build_index(self, index_name=None, index_config=None, raise_if_exist=False):
        if self.es.indices.exists(index=index_name or self.index_name) is not True:
            res = self.es.indices.create(
                index=index_name or self.index_name,
                body=index_config or self.index_config
            )
            return res
        else:
            msg = "Index [%s] already exits" % self.index_name
            if raise_if_exist:
                raise RuntimeError(msg)
            else:
                LOG.info(msg)
                return False

    def search(self, query, index_name=None, index_type=None):
        return self.es.search(index=index_name or self.index_name, doc_type=index_type or self.index_type, body=query)

    def msearch(self, body):
        return self.es.msearch(body=body)

    def insert(self, doc, index_name=None, index_type=None, id=None):
        return self.es.index(index=index_name or self.index_name, doc_type=index_type or self.index_type, id=id, body=doc)
