__all__ = ('Application',)

import asyncio

from ..logger import LOG

try:
    import uvloop
    from tornado.platform.asyncio import AsyncIOMainLoop

    asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())
    AsyncIOMainLoop().install()
    # asyncio.get_event_loop().run_forever()
    # ^ the line above should be replaced by the start function below.
    LOG.info('Using uvloop for service event loop...')
except ImportError:
    LOG.warn('[uvloop] NOT installed, fallback to asyncio loop! Please `pip install uvloop`!')

from .web import WebApplication
from ..settings import SETTINGS

from tornado.options import options

options['log_file_prefix'] = 'access.log'

io_loop = asyncio.get_event_loop()


class Application:
    def __init__(self, *args, **kwargs):
        settings = dict(SETTINGS.config)
        self.web_app = WebApplication(settings)
        self.io_loop = io_loop

    def start(self):
        try:
            self.web_app.start()
            self.io_loop.run_forever()
        except KeyboardInterrupt:
            pass
        except Exception as e:
            raise e
        finally:
            pass

    def stop(self):
        self.io_loop.stop()
