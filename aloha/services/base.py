import abc
import asyncio
from typing import Optional, Awaitable

from tornado import web, httpserver
from tornado.options import options
from tornado.routing import HostMatches


class Service(abc, web.RequestHandler):
    def response(self, *args, **kwargs) -> dict:
        raise NotImplementedError()

    def set_default_headers(self) -> None:
        self.set_header('Content-Type', 'application/json')

    def data_received(self, chunk: bytes) -> Optional[Awaitable[None]]:
        pass

    async def post(self):
        req = self.request.body
        resp = self.response(req)
        await self.finish(resp)


def start_application(list_url_handlers: list):
    application = web.Application([
        (HostMatches('(.*)'), list_url_handlers)
    ])
    server = httpserver.HTTPServer(application)
    server.bind(options.port)
    server.start(options.num_process)
    asyncio.get_event_loop().run_forever()
