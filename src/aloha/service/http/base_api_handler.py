import json
from abc import ABC
from datetime import datetime
from typing import Optional, Awaitable

from tornado import web

from ...logger import LOG


class AbstractApiHandler(web.RequestHandler, ABC):
    LOG = LOG
    MAP_ERROR_INFO: dict = {
        'BAD_REQUEST': {'code': '5101', 'message': ['Bad request: fail to parse body as JSON object!']}
    }

    def __init__(self, *args, **kwargs):
        self.api_args: Optional[tuple] = None
        self.api_kwargs: Optional[dict] = None
        super().__init__(*args, **kwargs)

    def on_finish(self) -> None:
        func_callback = getattr(self, 'callback', None)
        if callable(func_callback) \
                and isinstance(self.api_args, tuple) \
                and isinstance(self.api_kwargs, dict):
            func_callback(*self.api_args, **self.api_kwargs)

    def response(self, *args, **kwargs) -> dict:
        raise NotImplementedError()

    def set_default_headers(self) -> None:
        self.set_header('Content-Type', 'application/json; charset=utf-8')

    def data_received(self, chunk: bytes) -> Optional[Awaitable[None]]:
        pass

    @property
    def request_header_content_type(self) -> str:
        return self.request.headers.get('Content-Type', 'application/json; charset=utf-8')

    @property
    def request_id(self):
        if 'Request-ID' not in self.request.headers:
            self.request.headers['Request-ID'] = datetime.now().strftime('%Y%m%d-%H%M%S-%f')
        return self.request.headers.get('Request-ID')

    @property
    def request_body(self) -> dict:
        content_type: str = self.request_header_content_type
        body_arguments: dict = Optional[None]

        if content_type.startswith('multipart/form-data'):  # only parse files when 'Content-Type' starts with 'multipart/form-data'
            body_arguments = self.request.body_arguments
        else:
            try:
                body = self.request.body.decode('utf-8')
                body_arguments = json.loads(body)
            except (UnicodeDecodeError, json.decoder.JSONDecodeError):  # invalid request body, cannot be parsed as JSON
                self.finish(self.MAP_ERROR_INFO['BAD_REQUEST'])
        return body_arguments

    @property
    def request_param(self) -> dict:
        url_arguments: dict = {k: v[0].decode('utf-8') for k, v in self.request.arguments.items()}
        return url_arguments


class DefaultHandler404(AbstractApiHandler):
    def response(self, *args, **kwargs) -> Optional[dict]:
        return self.prepare()

    def prepare(self):  # for all methods
        msg = {
            "code": 404,
            "status": "error",
            "message": [
                'Requested URL cannot be found: %s' % self.request.uri
            ]
        }
        msg = json.dumps(msg, ensure_ascii=False, default=str, separators=(',', ':'))
        self.set_status(404, reason='Not Found')
        self.finish(msg)
