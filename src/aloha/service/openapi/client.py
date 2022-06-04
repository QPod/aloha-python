import json
from datetime import datetime, timedelta
from typing import Optional

from requests import Session
from requests.adapters import HTTPAdapter, Retry

from ...logger import LOG

try:
    from simplejson.errors import JSONDecodeError
except ImportError:
    from json import JSONDecodeError


class OpenApiClient:
    retry_method_whitelist = frozenset(['GET', 'POST'])
    retry_status_forcelist = frozenset({413, 429, 503, 502, 504})

    def __init__(self, url_oauth_get_token: str, client_id: str, client_secret: str, grant_type: str = 'client_credentials'):
        self.url_oauth_get_token = url_oauth_get_token
        self.client_id = client_id
        self.client_secret = client_secret
        self.grant_type = grant_type

        self.expires_at = None
        self.access_token = None

    @classmethod
    def get_request_session(cls, total_retries: int = 10, *args, **kwargs) -> Session:
        session = Session()
        # https://urllib3.readthedocs.io/en/latest/reference/urllib3.util.html#urllib3.util.Retry.DEFAULT_ALLOWED_METHODS
        retries = Retry(
            total=total_retries, backoff_factor=0.1, method_whitelist=cls.retry_method_whitelist, status_forcelist=cls.retry_status_forcelist
        )
        for prefix in ('http://', 'https://'):
            session.mount(prefix, HTTPAdapter(max_retries=retries))
        return session

    def get_access_token(self) -> str:
        now = datetime.now()

        if self.expires_at is None or self.expires_at > now:
            try:
                # refresh access_token
                resp = self.get_request_session().post(self.url_oauth_get_token, timeout=5, json={
                    'client_id': self.client_id,
                    'client_secret': self.client_secret,
                    'grant_type': self.grant_type
                })

                data = resp.json()['data']
                if data is None or 'access_token' not in data:
                    raise RuntimeError('Fail to fetch OpenAPI token with result: %s' % resp.text)

                self.access_token = data['access_token']

                expires_in = int(data['expires_in'])
                self.expires_at = datetime.now() + timedelta(minutes=expires_in - 1)
            except Exception as e:
                LOG.error('Exception acquiring ESG access token from [%s]: %s' % (self.url_oauth_get_token, str(e)))

        return self.access_token

    def _get_request_url(self, url: str):
        request_url = '{url}?access_token={access_token}&request_id={request_id}'.format(
            url=url, access_token=self.get_access_token(), request_id=datetime.now().strftime('%Y%m%d-%H%M%S-%f')
        )
        return request_url

    @staticmethod
    def _get_data_from_esg_response(resp) -> Optional[dict]:
        try:
            return resp.json()
        except (json.JSONDecodeError, JSONDecodeError):  # requests may use `simplejson`
            try:
                # when data is wrapped by ESG
                content = resp.text.replace('"data":"', '"data":').replace('}"}', '}}')
                data = json.loads(content)
                return data.get('data', {})
            except json.JSONDecodeError:
                msg = 'Cannot parse ESG response: %s' % resp.text
                raise ValueError(msg)

    def post(self, url_api: str, body: dict, headers: dict = None, timeout: int = 5):
        url = self._get_request_url(url_api)
        LOG.debug('Calling ESG POST: %s' % url)
        try:
            resp = self.get_request_session().post(url=url, headers=headers, json=body, timeout=timeout)
            return self._get_data_from_esg_response(resp)
        except Exception as e:
            LOG.error('Error calling ESG API POST [%s]: %s' % (url, str(e)))

    def get(self, url_api: str, body: dict, headers: dict = None, timeout: int = 5):
        url = self._get_request_url(url_api)
        LOG.debug('Calling ESG GET: %s' % url)
        try:
            resp = self.get_request_session().get(url=url, headers=headers, json=body, timeout=timeout)
            return self._get_data_from_esg_response(resp)
        except Exception as e:
            LOG.error('Error calling ESG API GET [%s]: %s' % (url, str(e)))
