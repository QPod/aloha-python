import json
import unittest
from abc import ABC

import requests

from ..logger import LOG
from ..service.caller import APICaller
from ..settings import SETTINGS


class ServiceTestCase(unittest.TestCase, ABC, APICaller):
    LOG = LOG
    api_url_base = SETTINGS.config.get('service', {}).get('port', 80)

    @classmethod
    def request_api(cls, api_url, timeout=5, **kwargs):
        """

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
