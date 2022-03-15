import uuid

import requests

from .param_check import sign_data
from ...logger import LOG
from ...settings import SETTINGS

APP_ID_KEYS = SETTINGS.config.get('APP_ID_KEYS', {})


class APICaller:
    @staticmethod
    def wrap_request_data(
            data, app_id: str = None, app_key: str = None, salt_uuid: str = None, sign: str = None, sign_method: str = None
    ):
        if app_id is None:
            # if len(APP_ID_KEYS) != 1:
            #     raise RuntimeError('Please specify 1 and only 1 in APP_ID_KEYS in configurations!')
            app_id = list(APP_ID_KEYS.keys())[0]
        salt_uuid = salt_uuid or str(uuid.uuid1())
        sign = sign or sign_data(
            salt_uuid=salt_uuid,
            app_id=app_id,
            app_key=app_key or APP_ID_KEYS.get(app_id),
            data=data,
            sign_method=sign_method
        )
        return {
            'salt_uuid': salt_uuid,
            'app_id': app_id,
            'sign': sign,
            'data': data
        }

    @staticmethod
    def call(api_url, timeout=5, **kwargs):
        """

        :param api_url: do NOT starts with slash (/)
        :param timeout: requests timeout in seconds
        :param kwargs: request data
        :return:
        """
        payload = APICaller.wrap_request_data(data=kwargs)
        LOG.debug('Calling API: %s' % api_url)
        resp = requests.post(
            api_url, json=payload, timeout=timeout, headers={'Content-Type': 'application/json'}
        ).json()
        ret = resp['data']
        return ret
