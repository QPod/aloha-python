__all__ = ('Application',)

import asyncio

from .web import WebApplication
from ..settings import SETTINGS


class Application:
    def __init__(self, *args, **kwargs):
        settings = dict(SETTINGS.config)
        self.web_app = WebApplication(settings)
        self.io_loop = asyncio.get_event_loop()

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
        def _stop():
            self.io_loop.stop()

        self.io_loop.call_soon(_stop)
