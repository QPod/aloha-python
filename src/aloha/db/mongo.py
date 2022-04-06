__all__ = ('MongoOperator',)

import ipaddress
import json

import pymongo

from .base import password_vault
from ..logger import LOG


def _is_ip_addr(s):
    try:
        ipaddress.ip_address(s)
        return True
    except ValueError:
        return False


_conn = {}


def MongoOperator(config):
    db_name = config.get('db_name')
    collection_name = config.get('collection_name')

    _config = {k: v for k, v in config.items() if v is not None}
    key = '%s:%s:%s' % (
        json.dumps(_config, sort_keys=True, ensure_ascii=False),
        db_name or '',
        collection_name or ''
    )

    if key not in _conn:
        try:
            _conn[key] = _MongoDBOperation(_config, db_name=db_name, collection_name=collection_name)
        except Exception as e:
            LOG.exception(e)
            return
    return _conn[key]


class _MongoDBOperation:
    def __init__(self, config, db_name=None, collection_name=None):
        self.db_name, self.collection_name = db_name, collection_name

        host = config['host']

        if config.get('port') is None and isinstance(host, list):
            hosts = ['{host}:{port}'.format(**h) for h in host]
        else:
            hosts = ['{host}:{port}'.format(host=host, port=config['port'])]

        replicaSet = config.get('replicaSet')
        if replicaSet is None and not _is_ip_addr(hosts[0].split(':')[0]):
            # if `replicaSet` not defined, and host in config is domain name (not IP)
            replicaSet = hosts[0].split('.')[0]  # use the first segment of domain name as replicaSet

        _config = {
            'host': 'mongodb://%s' % ','.join(hosts),
            'port': config.get('port'),
            'replicaSet': replicaSet,
            'username': config['username'],
            'password': password_vault.get_password(config.get('password')),
            'maxPoolSize': config.get('maxPoolSize'),
            'authSource': config.get('authSource', db_name)
        }
        LOG.debug(_config)

        try:
            self.conn = pymongo.MongoClient(**_config)

            self.db = self.conn[db_name]
            if self.collection_name is not None:
                self.collection = self.db[self.collection_name]
        except Exception as e:
            LOG.exception(e)

    def set_collection(self, collection_name):
        if collection_name not in self.db.list_collection_names():
            raise Exception("Collection[%s] does not exist in [%s]" % (self.collection_name, self.db_name))
        self.collection_name = collection_name
        self.collection = self.db[self.collection_name]
        return True

    def check_and_get_collection(self, collection_name=None, raise_if_not_exists=True):
        """
        检查collection是否存在，如果存在则返回collection对象，否则抛出异常
        Args:
            @param collection_name: str或unicode    collection名称
        Returns:
            @return: collection对象
        Raises:
            @raise Exception: 如果collection在对应db中不存在，则
        """
        self.db = self.conn[self.db_name]

        if self.collection_name is not None:
            self.collection = self.db[self.collection_name]

        if collection_name is not None and collection_name != self.collection_name:
            if self.collection_name not in self.db.list_collection_names():
                if raise_if_not_exists:
                    raise Exception("Collection [%s] does not exist in [%s]" % (self.collection_name, self.db_name))
                else:
                    pass

            self.collection_name = collection_name
            self.collection = self.db[self.collection_name]

        return self.collection

    def insert(self, doc_or_docs, check_keys=False, collection_name=None):
        try:
            collection = self.check_and_get_collection(collection_name)
            return collection.insert(doc_or_docs, check_keys=check_keys)
        except Exception as e:
            LOG.exception(e)

    def insert_many(self, docs, collection_name=None):
        try:
            collection = self.check_and_get_collection(collection_name)
            return collection.insert_many(docs)
        except Exception as e:
            LOG.exception(e)

    def insert_one(self, doc, collection_name=None):
        try:
            collection = self.check_and_get_collection(collection_name)
            return collection.insert_one(doc)
        except Exception as e:
            LOG.exception(e)

    def delete_many(self, field_filter, collection_name=None):
        try:
            collection = self.check_and_get_collection(collection_name)
            return collection.delete_many(filter=field_filter)
        except Exception as e:
            LOG.exception(e)

    def delete_one(self, field_filter, collection_name=None):
        try:
            collection = self.check_and_get_collection(collection_name)
            return collection.delete_one(filter=field_filter)
        except Exception as e:
            LOG.exception(e)

    def update_one(self, field_filter, update, upsert=False, bypass_document_validation=False,
                   collation=None, array_filters=None, session=None, collection_name=None):
        try:
            collection = self.check_and_get_collection(collection_name)
            collection.update_one(filter=field_filter, update=update, upsert=upsert, bypass_document_validation=bypass_document_validation,
                                  collation=collation, array_filters=array_filters, session=session)
            return True
        except Exception as e:
            LOG.exception(e)
            return False

    def update_many(self, field_filter, update, upsert=False, bypass_document_validation=False,
                    collation=None, array_filters=None, session=None, collection_name=None):
        try:
            collection = self.check_and_get_collection(collection_name)
            return collection.update_many(filter=field_filter, update=update, upsert=upsert, bypass_document_validation=bypass_document_validation,
                                          collation=collation, array_filters=array_filters, session=session)
        except Exception as e:
            LOG.exception(e)

    def query(self, field_filter=None, sort=None, limit=40, skip=0, collection_name=None):
        """
        从mongo查询数据
        Args:
            @param field_filter: dict     根据mongo查询语法构造查询条件
            @param sort: array      排序条件，例如：[("company_name",pymongo.ASCENDING), ("_id",pymongo.ASCENDING)]
            @param limit: int       查询条数
            @param skip: int        controls the starting point of the results set
            @param collection_name: str    collection名称，在建立完连接后可动态更换要查询的collection
        Returns:
            @return: 返回查询结果的游标对象
        """
        try:
            collection = self.check_and_get_collection(collection_name)
            if sort:
                result = collection.find(field_filter or {}).sort(sort).limit(limit)
            else:
                result = collection.find(field_filter or {}).skip(skip).limit(limit)
            return result
        except Exception as e:
            LOG.exception(e)

    def find_many(self, field_filter=None, projection=None, collection_name=None, *args, **kwargs):
        """
        从mongo查询数据，返回所有返回数据的游标
        Args:
            @param field_filter: dict     根据mongo查询语法构造查询条件
            @param projection: dict     限制返回的字段 exmaple: { name: 1, contribs: 1, _id: 0 }
            @param collection_name: str    collection名称，在建立完连接后可动态更换要查询的collection
        """
        try:
            collection = self.check_and_get_collection(collection_name)
            result = collection.find(field_filter or {}, projection, *args, **kwargs)
            return result
        except Exception as e:
            LOG.exception(e)

    def find_one(self, field_filter=None, projection=None, collection_name=None, *args, **kwargs):
        """
        从mongo查询数据,只返回单个结果
        Args:
            @param field_filter: dict     根据mongo查询语法构造查询条件
            @param projection: dict     限制返回的字段 exmaple: { name: 1, contribs: 1, _id: 0 }
            @param collection_name: str    collection名称，在建立完连接后可动态更换要查询的collection
        """
        try:
            collection = self.check_and_get_collection(collection_name)
            result = collection.find_one(field_filter or {}, projection, *args, **kwargs)
            return result
        except Exception as e:
            LOG.exception(e)

    def count(self, field_filter=None, collection_name=None):
        """
        从mongo查询数据条数
        Args:
            @param field_filter: dict    根据mongo查询语法构造查询条件
            @param collection_name: str    collection名称，在建立完连接后可动态更换要查询的collection
        """
        try:
            collection = self.check_and_get_collection(collection_name)
            result = collection.count_documents(field_filter or {})
            return result
        except Exception as e:
            LOG.exception(e)

    def check_connected(self):
        if not self.conn.connected:
            raise NameError('stat:connected Error')
