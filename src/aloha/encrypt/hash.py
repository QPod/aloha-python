import hashlib
import json


def get_md5_of_str(string):
    return hashlib.md5(string.encode()).hexdigest()


def get_sha256_of_str(string):
    return hashlib.sha256(string.encode()).hexdigest()


def hash_dict(dic):
    s = json.dumps(dict(dic), sort_keys=True, ensure_ascii=False, default=str)
    return hashlib.md5(s.encode()).hexdigest()


def hash_obj(obj):
    s = json.dumps(obj, sort_keys=True, ensure_ascii=False, default=str)
    return hashlib.md5(s.encode()).hexdigest()
