import abc
import json
import logging
from datetime import datetime
from typing import Optional, Awaitable

from tornado import web

from ...encrypt import jwt
from ...logger import LOG
from ...settings import SETTINGS

_RESP_BAD_REQUEST = {'code': '5101', 'message': ['Bad request: fail to parse body as JSON object!']}


class APIHandler(web.RequestHandler):
    LOG = LOG

    def __init__(self, *args, **kwargs):
        self.api_args: Optional[tuple] = None
        self.api_kwargs: Optional[dict] = None
        super().__init__(*args, **kwargs)

    @abc.abstractmethod
    def response(self, *args, **kwargs) -> dict:
        raise NotImplementedError()

    @property
    def request_id(self):
        if 'Request-ID' not in self.request.headers:
            self.request.headers['Request-ID'] = datetime.now().strftime('%Y%m%d-%H%M%S-%f')
        return self.request.headers.get('Request-ID')

    def set_default_headers(self) -> None:
        self.set_header('Content-Type', 'application/json; charset=utf-8')

    def data_received(self, chunk: bytes) -> Optional[Awaitable[None]]:
        pass

    def on_finish(self) -> None:
        func_callback = getattr(self, 'callback', None)
        if not callable(func_callback):
            return

        return func_callback(*self.api_args, **self.api_kwargs)

    async def prepare(self, ) -> Optional[Awaitable[None]]:
        access_token = self.request.headers.get('Access-Token')
        if access_token is None:
            return self.finish({
                'msg': 'Invalid Access-Token in request header!'
            })
        else:
            secret_key = SETTINGS.config['APP_SECRET_KEY']  # 'HCTECH-ASKBOB-REC:10062462'
            # options = None
            # TODO: if not validate expiration
            options = {"verify_exp": False}
            access_token = jwt.decode(secret_key, access_token, options=options)
            if not isinstance(access_token, dict):
                LOG.error('Invalid Access-Token found in request for [%s]: %s' % (
                    str(self.request.full_url()), access_token
                ))
                return self.finish({
                    'msg': access_token
                })

        self.set_header('Request-ID', self.request_id)

    async def post(self, *args, **kwargs):
        content_type: str = self.request.headers.get('Content-Type', 'application/json; charset=utf-8')
        if content_type.startswith('multipart/form-data'):  # only parse files when 'Content-Type' starts with 'multipart/form-data'
            body_arguments = self.request.body_arguments
        else:
            try:
                body = self.request.body.decode('utf-8')
                body_arguments = json.loads(body)
            except (UnicodeDecodeError, json.decoder.JSONDecodeError):  # invalid request body, cannot be parsed as JSON
                return self.finish(_RESP_BAD_REQUEST)
        kwargs.update(body_arguments)

        try:
            if self.LOG.level == logging.DEBUG:
                s_kwargs = json.dumps(kwargs, ensure_ascii=False)
                self.LOG.debug('POST Request [%s]: %s' % (self.request_id, s_kwargs[:1000]))
            self.api_args, self.api_kwargs = args or (), kwargs or {}
            resp = self.response(*self.api_args, **self.api_kwargs)  # this call may throw TypeError when argument missing
        except Exception as e:
            self.LOG.error(e, exc_info=True)
            self.LOG.info('POST Request [%s]: %s' % (self.request_id, self.request.body))
            return self.finish({'status': 'error', 'message': [str(e)]})

        if isinstance(resp, (dict, list)):
            resp = json.dumps(resp, ensure_ascii=False, default=str, separators=(',', ':'))
        elif isinstance(resp, str):
            pass
        return self.finish(resp)

    async def get(self, *args, **kwargs):
        query = {k: v[0].decode('utf-8') for k, v in self.request.arguments.items()}
        kwargs.update(query)
        try:
            self.LOG.debug('GET Request [%s]: %s' % (self.request_id, kwargs))
            self.api_args, self.api_kwargs = args or (), kwargs or {}
            resp = self.response(*self.api_args, **self.api_kwargs)  # this call may throw TypeError when argument missing
        except Exception as e:
            self.LOG.error(e, exc_info=True)
            self.LOG.info('GET Request [%s]: %s' % (self.request_id, kwargs))
            return self.finish({'status': 'error', 'message': [repr(e)]})

        if isinstance(resp, (dict, list)):
            resp = json.dumps(resp, ensure_ascii=False, default=str, separators=(',', ':'))
        elif isinstance(resp, str):
            pass
        return self.finish(resp)
