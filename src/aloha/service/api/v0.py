__all__ = ('APIHandler', 'APICaller',)

import json
import logging
from abc import ABC

from ..http import AbstractApiClient, AbstractApiHandler


class APIHandler(AbstractApiHandler, ABC):
    MAP_ERROR_INFO = {
        'BAD_REQUEST': {'code': '5101', 'message': ['Bad request: fail to parse body as JSON object!']}
    }

    async def post(self, *args, **kwargs):
        body_arguments = self.request_body
        kwargs.update(body_arguments)

        resp = dict(code=5200, message=['success'])
        try:
            result = self.response(*args, **kwargs)  # this call may throw TypeError when argument missing
            resp['data'] = result
        except Exception as e:
            if self.LOG.level == logging.DEBUG:
                self.LOG.error(e, exc_info=True)
            return self.finish({'code': 5201, 'message': [repr(e)]})

        resp = json.dumps(resp, ensure_ascii=False, default=str, separators=(',', ':'))
        return self.finish(resp)


class APICaller(AbstractApiClient):
    def wrap_request_data(self, data: dict) -> dict:
        assert isinstance(data, dict), "Data object must be a dict!"
        return data
