import requests
from requests.adapters import HTTPAdapter, Retry

from ...logger import LOG


class APICaller:
    retry_method_whitelist = frozenset(['GET', 'POST'])
    retry_status_forcelist = frozenset({413, 429, 503, 502, 504})

    @classmethod
    def get_request_session(cls, total_retries: int = 3, *args, **kwargs) -> requests.Session:
        session = requests.Session()
        # https://urllib3.readthedocs.io/en/latest/reference/urllib3.util.html#urllib3.util.Retry.DEFAULT_ALLOWED_METHODS
        retries = Retry(
            total=total_retries, backoff_factor=0.1, method_whitelist=cls.retry_method_whitelist, status_forcelist=cls.retry_status_forcelist
        )
        for prefix in ('http://', 'https://'):
            session.mount(prefix, HTTPAdapter(max_retries=retries))
        return session

    @staticmethod
    def wrap_request_data(data):
        assert isinstance(data, dict), "Data object must be a dict!"
        return data

    def call(self, api_url, timeout=5, **kwargs):
        """Trigger API call

        :param api_url: do NOT start with slash (/)
        :param timeout: requests timeout in seconds
        :param kwargs: request data
        :return:
        """
        payload = APICaller.wrap_request_data(data=kwargs)
        LOG.debug('Calling API: %s' % api_url)
        session = self.get_request_session()
        resp = session.post(
            api_url, json=payload, timeout=timeout, headers={'Content-Type': 'application/json'}
        )

        try:
            ret = resp.json()
        except Exception as e:
            LOG.error(str(e))
            raise RuntimeError(resp.text)

        try:
            return ret['data']
        except KeyError:
            raise RuntimeError(resp.text)
