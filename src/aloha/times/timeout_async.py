import asyncio
from functools import wraps, partial

__all__ = ('timeout',)


def aioify(func):
    @wraps(func)
    async def run(*args, loop=None, executor=None, **kwargs):
        if loop is None:
            loop = asyncio.get_event_loop()
        p_func = partial(func, *args, **kwargs)
        return await loop.run_in_executor(executor, p_func)

    return run


def timeout(func, timeout=1):
    async def f():
        try:
            result = await asyncio.wait_for(aioify(func), timeout=timeout)
            return result
        except asyncio.TimeoutError:
            raise TimeoutError()
    return f
