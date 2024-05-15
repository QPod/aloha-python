from aloha.logger import LOG
from aloha.service.api.v0 import APIHandler


class MultipartHandler(APIHandler):
    def response(self, params=None, *args, **kwargs):
        LOG.debug(params)
        return params


default_handlers = [
    # internal API: QueryDB Postgres with sql directly
    (r"/api_internal/multipart", MultipartHandler),
]
