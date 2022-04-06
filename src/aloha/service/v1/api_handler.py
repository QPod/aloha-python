import abc
import json
import logging
from typing import Optional, Awaitable

from tornado import web

from .param_check import sign_check
from ...logger import LOG

_RESP_BAD_REQUEST = {'code': '5101', 'message': ['Bad request: fail to parse body as JSON object!']}
_RESP_MISSING_ARGS = {'code': '5102', 'message': ['Required argument field(s) missing...']}
_RESP_SIGN_CHECK_FAIL = {'code': '5104', 'message': ['Invalid sign, sign check failed!']}


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

    async def post(self):
        try:
            req = self.request.body
            body = json.loads(req.decode('utf-8'))
        except json.decoder.JSONDecodeError:  # invalid request body, cannot be parsed as JSON
            return self.finish(_RESP_BAD_REQUEST)

        try:
            salt_uuid = body.pop('salt_uuid')
            app_id = body.pop('app_id')
            sign = body.pop('sign')
            data = body.pop('data')
        except KeyError:  # cannot find default key from parsed body
            return self.finish(_RESP_MISSING_ARGS)

        is_valid_req = sign_check(salt_uuid=salt_uuid, app_id=app_id, sign=sign, data=data)  # , sign_method='sha256'
        if not is_valid_req:
            return self.finish(_RESP_SIGN_CHECK_FAIL)

        resp = dict(code=5200, message=['success'])
        try:
            result = self.response(**data)  # this call may throw TypeError when argument missing
            resp['data'] = result
            resp['salt_uuid'] = salt_uuid
        except Exception as e:
            if LOG.level == logging.DEBUG:
                self.LOG.error(e, exc_info=True)
            return self.finish({'code': 5201, 'message': [str(e)]})

        resp = json.dumps(resp, ensure_ascii=False, default=str, separators=(',', ':'))
        return self.finish(resp)
