import logging
import os
import socket
from os.path import join as pjoin

from .handler import MultiProcessSafeDailyRotatingFileHandler


def setup_logger(logger: logging.Logger, level: int = logging.DEBUG, logger_name: str = None, module: str = None, formatter_str: str = None):
    if not logger.handlers:
        formatter = logging.Formatter(formatter_str or '%(levelname)s> %(asctime)s> %(module)s:%(lineno)s> %(message)s')

        folder = os.environ.get('DIR_LOG', 'logs')
        os.makedirs(folder, exist_ok=True)

        if module is None:
            from ..settings import SETTINGS
            module = SETTINGS.config.get('APP_MODULE') or os.environ.get('APP_MODULE', 'default')

        if logger_name is not None and len(logger_name) > 0:
            module = '%s_%s' % (logger_name, module)

        path_file = [module, socket.gethostname(), 'p%s' % os.getpid()]  # module, hostname, pid
        path_file = '_'.join(str(i) for i in path_file if i is not None)
        path_file = pjoin(folder, '%s.log' % path_file)
        file_handler = MultiProcessSafeDailyRotatingFileHandler(path_file)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

        stream_handler = logging.StreamHandler()
        stream_handler.setFormatter(formatter)
        logger.addHandler(stream_handler)

        logger.setLevel(level)


def get_logger(level=logging.DEBUG, logger_name: str = None, *args, **kwargs) -> logging.Logger:
    logger = logging.getLogger(logger_name)

    if isinstance(level, str):
        level = getattr(logging, str(level).upper(), 10)

    setup_logger(logger, level=level, logger_name=logger_name, *args, **kwargs)
    return logger
