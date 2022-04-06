import json
from abc import ABC

import requests

from .unit import UnitTestCase
from ..service.v1 import APICaller


class ServiceTestCase(UnitTestCase, ABC, APICaller):
    api_url_base = None

    @classmethod
    def setUpClass(cls) -> None:
        cls.api_url_base = ServiceTestCase.config.get('service', {}).get('port', 80)

    @classmethod
    def request_api(cls, api_url, timeout=5, **kwargs):
        """Class method to test an API call

        :param api_url: do NOT starts with slash (/)
        :param timeout: requests timeout in seconds
        :param kwargs: request data
        :return:
        """
        payload = cls.wrap_request_data(data=kwargs)
        url = 'http://localhost:%s/%s' % (cls.api_url_base, api_url)
        cls.LOG.debug("POST %s  %s" % (url, json.dumps(payload, ensure_ascii=False, sort_keys=True)))
        resp = requests.post(
            url, json=payload, timeout=timeout, headers={'Content-Type': 'application/json'}
        ).json()
        cls.LOG.debug(resp)
        return resp
