"""Easily put time restrictions on things
Note: Requires Python 3.x
Usage as a context manager:
```
with TimeOutRestriction(10):
    something_that_should_not_exceed_ten_seconds()
```
Usage as a decorator:
```
@TimeOutRestriction(10)
def something_that_should_not_exceed_ten_seconds():
    do_stuff_with_a_timeout()
```
Handle timeouts:
```
try:
   with TimeOutRestriction(10):
       something_that_should_not_exceed_ten_seconds()
   except TimeoutError:
       log('Got a timeout, couldn't finish')
```
Suppress TimeoutError and just die after expiration:
```
with TimeOutRestriction(10, suppress_timeout_errors=True):
    something_that_should_not_exceed_ten_seconds()
print('Maybe exceeded 10 seconds, but finished either way')
```
"""
import contextlib
import errno
import os
import signal

DEFAULT_TIMEOUT_MESSAGE = os.strerror(errno.ETIME)


class TimeOutRestriction(contextlib.ContextDecorator):
    def __init__(self, milliseconds: float, *, timeout_message: str = DEFAULT_TIMEOUT_MESSAGE, suppress_timeout_errors: bool = False):
        self.millisecond = milliseconds
        self.timeout_message = timeout_message
        self.suppress = bool(suppress_timeout_errors)

    def _timeout_handler(self, signum, frame):
        raise TimeoutError(self.timeout_message)

    def __enter__(self):
        signal.signal(signal.SIGALRM, self._timeout_handler)
        signal.setitimer(signal.ITIMER_REAL, self.millisecond / 1000)

    def __exit__(self, exc_type, exc_val, exc_tb):
        signal.setitimer(signal.ITIMER_REAL, 0, 0)
        if self.suppress and exc_type is TimeoutError:
            return True
