import abc
import json
import logging
from typing import Optional, Awaitable

from tornado import web

from ...logger import LOG

_RESP_BAD_REQUEST = {'code': '5101', 'message': ['Bad request: fail to parse body as JSON object!']}


class APIHandler(web.RequestHandler):
    LOG = LOG

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    @abc.abstractmethod
    def response(self, *args, **kwargs) -> dict:
        raise NotImplementedError()

    def set_default_headers(self) -> None:
        self.set_header('Content-Type', 'application/json; charset=utf-8')

    def data_received(self, chunk: bytes) -> Optional[Awaitable[None]]:
        pass

    async def post(self, *args, **kwargs):
        try:
            req = self.request.body
            body = json.loads(req.decode('utf-8'))
            kwargs.update(body)
        except json.decoder.JSONDecodeError:  # invalid request body, cannot be parsed as JSON
            return self.finish(_RESP_BAD_REQUEST)

        resp = dict(code=5200, message=['success'])
        try:
            result = self.response(*args, **kwargs)  # this call may throw TypeError when argument missing
            resp['data'] = result
        except Exception as e:
            if LOG.level == logging.DEBUG:
                self.LOG.error(e, exc_info=True)
            return self.finish({'code': 5201, 'message': [str(e)]})

        resp = json.dumps(resp, ensure_ascii=False, default=str, separators=(',', ':'))
        return self.finish(resp)
