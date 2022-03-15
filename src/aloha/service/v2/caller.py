import requests
import uuid
from datetime import datetime, timedelta

from ...encrypt.jwt import encode
from ...logger import LOG
from ...settings import SETTINGS

APP_ID_KEYS = SETTINGS.config.get('APP_ID_KEYS', {})
APP_SECRET_KEY = SETTINGS.config['APP_SECRET_KEY']


class APICaller:
    @staticmethod
    def get_headers(app_id: str = None, app_key: str = None) -> dict:
        if app_id is None:
            # if len(APP_ID_KEYS) != 1:
            #     raise RuntimeError('Please specify 1 and only 1 in APP_ID_KEYS in configurations!')
            app_id = list(APP_ID_KEYS.keys())[0]

        expire_time = datetime.now() + timedelta(days=1)

        access_token = encode(
            secret_key=APP_SECRET_KEY,
            payload={
                'exp': int(expire_time.timestamp()),
                'aid': app_id
            }
        )

        headers = {
            'Content-Type': 'application/json',
            'Access-Token': access_token,
            'Request-ID': str(uuid.uuid1()),
        }
        return headers

    @classmethod
    def call(cls, api_url, timeout=5, **kwargs) -> str:
        """

        :param api_url: do NOT start with slash (/)
        :param timeout: requests timeout in seconds
        :param kwargs: request data
        :return:
        """
        LOG.debug('Calling API: %s' % api_url)
        # LOG.debug('Param: %s' % json.dumps(kwargs, ensure_ascii=False))
        resp = requests.post(
            api_url,
            json=kwargs,
            timeout=timeout,
            headers=cls.get_headers()
        ).json()
        return resp
