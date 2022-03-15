from tornado import web
from typing import Optional, Awaitable


class BaseHandler(web.RequestHandler):
    def data_received(self, chunk: bytes) -> Optional[Awaitable[None]]:
        pass

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def set_default_headers(self):
        self.set_header('Access-Control-Allow-Origin', '*')
        self.set_header('Access-Control-Allow-Headers', '*')
        self.set_header('Access-Control-Max-Age', 1000)
        self.set_header('Content-type', 'application/json; charset=UTF-8')
        self.set_header('Access-Control-Allow-Methods', 'POST, GET, OPTIONS')
        self.set_header(
            'Access-Control-Allow-Headers',
            'authorization, Authorization, Content-Type,'
            'Access-Control-Allow-Origin, Access-Control-Allow-Headers,'
            'X-Requested-By, Access-Control-Allow-Methods'
        )
