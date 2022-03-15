__all__ = ('sign_data', 'sign_check')

import json

from ...encrypt.hash import get_md5_of_str, get_sha256_of_str
from ...settings import SETTINGS

APP_ID_KEYS = SETTINGS.config.get('APP_ID_KEYS', {})

APP_OPTIONS = SETTINGS.config.get('APP_OPTIONS', {})

FUNC_SIGN_CHECK = {'md5': get_md5_of_str, 'sha256': get_sha256_of_str}

func_sign_check_default = FUNC_SIGN_CHECK.get(APP_OPTIONS.get('sign_method', 'md5'))


def sign_data(salt_uuid: str, app_id: str, app_key: str, data, sign_method: str = None):
    data_str = str(json.dumps(data, ensure_ascii=False, sort_keys=True, separators=(',', ':')))
    public_key = app_id + salt_uuid + data_str + app_key

    func_sign_check = func_sign_check_default if sign_method is None else FUNC_SIGN_CHECK.get(sign_method)
    if func_sign_check is None:
        raise ValueError('Invalid `sign_method`: %s' % sign_method)
    sign = func_sign_check(public_key)
    return sign


def sign_check(salt_uuid: str, app_id: str, sign: str, data, sign_method: str = None, date_time=None):
    """签名验证
    :param salt_uuid: 通用唯一识别码，（1）用于生成签名；（2）方便追踪日志
    :param app_id: APP ID
    :param sign: 签名，app_id+salt_uuid+ data +密钥 的hash函数值
    :param data: data object, will be serialized to JSON string
    :param date_time: not used for now
    :param sign_method: Sign method, one of the following: md5, sha256
    :return: 签名验证通过， 返回True，否则返回False
    """

    func_sign_check = func_sign_check_default if sign_method is None else FUNC_SIGN_CHECK.get(sign_method)
    if func_sign_check is None:
        raise ValueError('Invalid `sign_method`: %s' % sign_method)

    app_key = APP_ID_KEYS.get(app_id)
    if app_key is None:  # APP_ID not in the dict, unknown APP_ID
        return False

    data_str = str(json.dumps(data, ensure_ascii=False, sort_keys=True, separators=(',', ':')))

    # --> 兼容智慧城早期API # TODO: 让智慧城改掉API签名方式
    right_sign = func_sign_check(app_id + salt_uuid + app_key)
    if sign == right_sign:
        return True
    # <--

    public_key = str(json.dumps(data, ensure_ascii=False, sort_keys=True, separators=(',', ':')))
    public_key = app_id + salt_uuid + public_key + app_key
    right_sign = func_sign_check(public_key)
    return sign == right_sign
