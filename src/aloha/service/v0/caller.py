import requests

from ...logger import LOG


class APICaller:
    @staticmethod
    def wrap_request_data(data):
        assert isinstance(data, dict), "Data object must be a dict!"
        return data

    @staticmethod
    def call(api_url, timeout=5, **kwargs):
        """Trigger API call

        :param api_url: do NOT start with slash (/)
        :param timeout: requests timeout in seconds
        :param kwargs: request data
        :return:
        """
        payload = APICaller.wrap_request_data(data=kwargs)
        LOG.debug('Calling API: %s' % api_url)
        resp = requests.post(
            api_url, json=payload, timeout=timeout, headers={'Content-Type': 'application/json'}
        )

        try:
            ret = resp.json()
        except Exception as e:
            LOG.error(str(e))
            raise RuntimeError(resp.text)

        try:
            return ret['data']
        except KeyError:
            raise RuntimeError(resp.text)
