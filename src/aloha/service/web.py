import os

from tornado import web, httpserver
from tornado.routing import HostMatches

from ..logger import LOG


def _load_handlers(name):
    """Load the (URL pattern, handler) tuples for each component."""
    mod = __import__(name, fromlist=['default_handlers'])
    return mod.default_handlers


class WebApplication(web.Application):
    def __init__(self, config: dict, *args, **kwargs):
        handlers = self.init_handlers(config)
        super().__init__(handlers, **config)

        self.http_server = httpserver.HTTPServer(self)

    def init_handlers(self, config: dict):
        settings = config.get('service', {})
        modules = settings.get('modules', [])
        handlers = []
        for m in modules:
            _handlers = _load_handlers(m)
            for h in _handlers:
                url = h[0]
                LOG.debug('Loading handler for API: %s' % url)
            handlers.extend(_handlers)

        return [
            (HostMatches('(.*)'), handlers)
        ]

    def start(self):
        service_settings = self.settings.get('service', {})

        port = service_settings.get('port', 80)
        # if overwrite port in param
        port = os.environ.get('port', port)

        num_process = service_settings.get('num_process', 1)
        LOG.info('Starting service at port [%s]...' % port)
        self.http_server.bind(port)
        self.http_server.start(num_processes=num_process)
