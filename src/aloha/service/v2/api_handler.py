import abc
import json
import logging
from datetime import datetime
from tornado import web
from typing import Optional, Awaitable

from ...encrypt import jwt
from ...logger import LOG
from ...settings import SETTINGS

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

    def on_finish(self) -> None:
        func_callback = getattr(self, 'callback', None)
        if not callable(func_callback):
            return

        body = json.loads(self.request.body.decode('utf-8'))
        return func_callback(**body)

    async def prepare(self, ) -> Optional[Awaitable[None]]:
        access_token = self.request.headers.get('Access-Token')
        if access_token is None:
            return self.finish({
                'msg': 'Invalid Access-Token in request header!'
            })
        else:
            secret_key = SETTINGS.config['APP_SECRET_KEY']  # 'HCTECH-ASKBOB-REC:10062462'
            access_token = jwt.decode(secret_key, access_token)
            if not isinstance(access_token, dict):
                return self.finish({
                    'msg': access_token
                })

    async def get(self, *args, **kwargs):
        query = {k: v[0].decode('utf-8') for k, v in self.request.arguments.items()}
        request_id = self.request.headers.get('Request-ID')
        if request_id is None:
            request_id = datetime.now().strftime('%Y%m%d-%H%M%S-%f')

        try:
            self.LOG.debug('GET Request [%s]: %s' % (request_id, query))
            resp = self.response(**query)  # this call may throw TypeError when argument missing
        except Exception as e:
            self.LOG.error(e, exc_info=True)
            self.LOG.info('POST Request [%s]: %s' % (request_id, query))
            return self.finish({'status': 'error', 'message': [str(e)]})

        resp = json.dumps(resp, ensure_ascii=False, default=str, separators=(',', ':'))
        return self.finish(resp)

    async def post(self, *args, **kwargs):
        try:
            body = self.request.body.decode('utf-8')
            data = json.loads(body)
        except json.decoder.JSONDecodeError:  # invalid request body, cannot be parsed as JSON
            return self.finish(_RESP_BAD_REQUEST)

        request_id = self.request.headers.get('Request-ID')
        if request_id is None:
            request_id = datetime.now().strftime('%Y%m%d-%H%M%S-%f')

        try:
            if self.LOG.level == logging.DEBUG:
                if len(body) < 1000:
                    self.LOG.debug('POST Request [%s]: %s' % (request_id, data))
                else:  # when body is too long, just print first 1000 char
                    self.LOG.debug('POST Request [%s]: %s' % (request_id, body[:1000]))
            resp = self.response(**data)  # this call may throw TypeError when argument missing
        except Exception as e:
            self.LOG.error(e, exc_info=True)
            self.LOG.info('POST Request [%s]: %s' % (request_id, data))
            return self.finish({'status': 'error', 'message': [str(e)]})

        resp = json.dumps(resp, ensure_ascii=False, default=str, separators=(',', ':'))
        return self.finish(resp)
