import logging
import os

from tornado import web, httpserver
from tornado.routing import HostMatches

from ..logger import LOG
from ..logger.logger import setup_logger
from ..settings import SETTINGS

setup_logger(
    logging.getLogger("tornado.access")
    , formatter_str='A> %(asctime)s> %(message)s'
    , module='access_%s' % (SETTINGS.config.get('APP_MODULE') or os.environ.get('APP_MODULE', 'default'))
)


def _load_handlers(name):
    """Load the (URL pattern, handler) tuples for each component."""
    mod = __import__(name, fromlist=['default_handlers'])
    handlers = []
    for url, handler in mod.default_handlers:

        if not url.startswith('/'):
            url = '/' + url
        handlers.append((url, handler))
    return handlers


class WebApplication(web.Application):
    def __init__(self, config: dict, *args, **kwargs):
        handlers = self.init_handlers(config)
        super().__init__(handlers=handlers, **config)
        self.http_server = httpserver.HTTPServer(self)

    @staticmethod
    def init_handlers(config: dict):
        settings = config.get('service', {})
        modules = settings.get('modules', [])
        handlers = []
        for m in modules:
            _handlers = _load_handlers(m)
            for h in _handlers:
                handlers.append(h)
                LOG.debug('Loaded module %s handler for API:\t%s' % h[::-1])

        return [
            (HostMatches('(.*)'), handlers)
        ]

    def start(self):
        service_settings = self.settings.get('service', {})

        port = service_settings.get('port', 80)
        # if overwrite port in param
        port = os.environ.get('port', port)

        num_process = int(service_settings.get('num_process', 1))
        LOG.info('Starting service with [%s] process at port [%s]...', num_process, port)
        self.http_server.bind(port)
        self.http_server.start(num_processes=num_process)
