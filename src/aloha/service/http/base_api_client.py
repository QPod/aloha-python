import uuid
from abc import ABC, abstractmethod
from urllib.parse import urljoin

import requests
from requests.adapters import HTTPAdapter, Retry

from ...logger import LOG
from ...settings import SETTINGS


class AbstractApiClient(ABC):
    LOG = LOG
    RETRY_METHOD_WHITELIST: frozenset = frozenset(['GET', 'POST'])
    RETRY_STATUS_FORCELIST: frozenset = frozenset({413, 429, 503, 502, 504})
    config = SETTINGS.config

    def __init__(self, url_endpoint: str = None, *args, **kwargs):
        self.url_endpoint = url_endpoint or ''
        LOG.debug('API Caller URL endpoint set to: %s' % self.url_endpoint)

    @classmethod
    def get_request_session(cls, total_retries: int = 3, *args, **kwargs) -> requests.Session:
        session = requests.Session()
        # https://urllib3.readthedocs.io/en/latest/reference/urllib3.util.html#urllib3.util.Retry.DEFAULT_ALLOWED_METHODS
        retries = Retry(
            total=total_retries, backoff_factor=0.1, method_whitelist=cls.RETRY_METHOD_WHITELIST, status_forcelist=cls.RETRY_STATUS_FORCELIST
        )
        for prefix in ('http://', 'https://'):
            session.mount(prefix, HTTPAdapter(max_retries=retries))
        return session

    def get_headers(self, *args, **kwargs) -> dict:
        headers = {
            'Content-Type': 'application/json',
            'Request-ID': str(uuid.uuid1()),
        }
        return headers

    @abstractmethod
    def wrap_request_data(self, data: dict) -> dict:
        assert isinstance(data, dict), "Data object must be a dict!"
        raise NotImplementedError()
        # return data

    def call(self, api_url: str, data: dict = None, timeout=5, **kwargs):
        """Trigger API call
        :param api_url: do NOT start with slash (/)
        :param data: a dictionary which includes the request data
        :param timeout: requests timeout in seconds
        :param kwargs: keywords arguments which will be updated to data
        :return:
        """
        body = data or dict()
        body.update(kwargs)
        payload = self.wrap_request_data(data=body)
        LOG.debug('Calling api: %s' % api_url)
        session = self.get_request_session()
        resp = session.post(
            urljoin(self.url_endpoint, api_url), json=payload, timeout=timeout, headers=self.get_headers()
        )

        try:
            ret = resp.json()
        except Exception as e:
            LOG.error(str(e))
            raise RuntimeError(resp.text)

        return ret
