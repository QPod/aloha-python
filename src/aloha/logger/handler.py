import time
from logging import StreamHandler
from logging.handlers import BaseRotatingHandler


class MultiProcessSafeDailyRotatingFileHandler(BaseRotatingHandler):
    """Similar with `logging.TimedRotatingFileHandler`, while this one is
    - Multi process safe
    - Rotate at midnight only
    - Utc not supported
    """

    def __init__(self, filename: str, encoding='utf8', delay=False, utc=False, **kwargs):
        self.utc = utc
        self.suffix = "%Y-%m%d"
        self.baseFilename = filename
        self.currentFileName = self._compute_fn()
        BaseRotatingHandler.__init__(self, filename, 'a', encoding, delay)

    def shouldRollover(self, record):
        if self.currentFileName != self._compute_fn():
            return True
        return False

    def doRollover(self):
        if self.stream:
            self.stream.close()
            self.stream = None
        self.currentFileName = self._compute_fn()
        if not self.delay:
            self.stream = self._open()

    def _compute_fn(self):
        return self.baseFilename.replace(".log", "") + "_" \
               + time.strftime(self.suffix, time.localtime()) \
               + '.log'

    def _open(self):
        return open(self.currentFileName, mode=self.mode, encoding=self.encoding)

    def close(self):
        """Closes the stream."""
        self.acquire()
        try:
            try:
                if self.stream:
                    try:
                        self.flush()
                    finally:
                        stream = self.stream
                        self.stream = None
                        if hasattr(stream, "close"):
                            # print('ttt')
                            stream.close()
            finally:
                # Issue #19523: call unconditionally to prevent a handler leak when delay is set
                StreamHandler.close(self)
        finally:
            self.release()
