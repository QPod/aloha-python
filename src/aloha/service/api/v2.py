__all__ = ('APIHandler', 'APICaller',)

import json
import logging
from abc import ABC
from datetime import datetime, timedelta
from typing import Optional, Awaitable

from ..http import AbstractApiClient, AbstractApiHandler
from ...encrypt import jwt
from ...settings import SETTINGS


class APIHandler(AbstractApiHandler, ABC):
    async def prepare(self, ) -> Optional[Awaitable[None]]:
        access_token = self.request.headers.get('Access-Token')
        if access_token is None:
            return self.finish({
                'msg': 'Invalid Access-Token in request header!'
            })
        else:
            secret_key = SETTINGS.config['APP_SECRET_KEY']
            # options = None
            # TODO: if not validate expiration
            options = {"verify_exp": False}
            access_token = jwt.decode(secret_key, access_token, options=options)
            if not isinstance(access_token, dict):
                self.LOG.error('Invalid Access-Token found in request for [%s]: %s' % (
                    str(self.request.full_url()), access_token
                ))
                return self.finish({
                    'msg': access_token
                })
        self.set_header('Request-ID', self.request_id)

    async def post(self, *args, **kwargs):
        body_arguments = self.request_body
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
        return self.finish(resp)

    async def get(self, *args, **kwargs):
        query_arguments = self.request_param
        kwargs.update(query_arguments)
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
        return self.finish(resp)


class APICaller(AbstractApiClient):
    APP_ID_KEYS = AbstractApiClient.config.get('APP_ID_KEYS', {})
    APP_SECRET_KEY = AbstractApiClient.config.get('APP_SECRET_KEY')

    def wrap_request_data(self, data: dict) -> dict:
        assert isinstance(data, dict), "Data object must be a dict!"
        return data

    def get_headers(self, app_id: str = None, app_key: str = None) -> dict:
        if app_id is None:
            # if len(APP_ID_KEYS) != 1:
            #     raise RuntimeError('Please specify 1 and only 1 in APP_ID_KEYS in configurations!')
            app_id = list(self.APP_ID_KEYS.keys())[0]

        expire_time = datetime.now() + timedelta(days=1)

        access_token = jwt.encode(
            secret_key=self.APP_SECRET_KEY,
            payload={
                'exp': int(expire_time.timestamp()),
                'aid': app_id
            }
        )

        headers = super().get_headers()
        headers.update({'Access-Token': access_token})
        return headers
