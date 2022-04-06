from abc import ABC

from .unit import UnitTestCase
from ..service.v2 import APICaller


class ServiceTestCase(UnitTestCase, ABC, APICaller):
    api_url_base = None

    @classmethod
    def setUpClass(cls) -> None:
        cls.api_url_port = ServiceTestCase.config.get('service', {}).get('port', 80)

    @classmethod
    def request_api(cls, api_url, timeout=5, **kwargs):
        """Class method to test an API call

        :param api_url: do NOT start with slash (/)
        :param timeout: requests timeout in seconds
        :param kwargs: request data
        :return:
        """
        url = 'http://localhost:%s/%s' % (cls.api_url_port, api_url)
        # cls.LOG.debug("POST %s  %s" % (url, json.dumps(kwargs, ensure_ascii=False, sort_keys=True)))
        # resp = requests.post(
        #     url, json=kwargs, timeout=timeout, headers={'Content-Type': 'application/json'}
        # ).json()
        # cls.LOG.debug(resp)
        return cls.call(url, timeout=timeout, **kwargs)
