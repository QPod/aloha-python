import copy
import logging
import logging.config
import os.path

from .handler import MultiProcessSafeDailyRotatingFileHandler


def setup_logging(log_config, level=logging.DEBUG):
    """Setup logging configuration"""
    _logger = logging.getLogger('base_logger')
    if _logger.handlers:
        for handler in _logger.handlers:
            handler.close()
    if _logger.filters:
        for tmp_filter in _logger.filters:
            _logger.removeFilter(tmp_filter)

    if log_config is not None and len(log_config) > 0:
        logging.config.dictConfig(log_config)
    else:
        _logger = logging.getLogger('base_logger')
        folder = 'logs'
        os.makedirs(folder, exist_ok=True)
        file_handler = MultiProcessSafeDailyRotatingFileHandler(
            os.path.join(folder, 'default_configs.log'),
            encoding='utf8'
        )
        file_handler.setLevel(level)
        formatter = logging.Formatter(
            '%(levelname)s [%(process)d @ %(asctime)s] %(module)s:%(lineno)s > %(message)s'
        )
        file_handler.setFormatter(formatter)
        _logger.addHandler(file_handler)

        stream_handler = logging.StreamHandler()
        stream_handler.setLevel(level)
        stream_handler.setFormatter(formatter)
        _logger.addHandler(stream_handler)
        _logger.setLevel(level)


def get_logger(level=logging.DEBUG):
    _logger = logging.getLogger('base_logger')
    if not _logger.handlers:
        folder = 'logs'
        os.makedirs(folder, exist_ok=True)
        file_handler = MultiProcessSafeDailyRotatingFileHandler(
            os.path.join(folder, 'default_configs.log'),
            encoding='utf8'
        )
        file_handler.setLevel(level)
        formatter = logging.Formatter(
            '%(levelname)s [%(process)d @ %(asctime)s] %(module)s:%(lineno)s > %(message)s'
        )
        file_handler.setFormatter(formatter)
        _logger.addHandler(file_handler)

        stream_handler = logging.StreamHandler()
        stream_handler.setLevel(level)
        stream_handler.setFormatter(formatter)
        _logger.addHandler(stream_handler)
        _logger.setLevel(level)

    _logger = logging.getLogger('base_logger')
    return _logger


def logger_setup(app_log_config, default_log_config):
    set_log_config = copy.deepcopy(default_log_config)
    set_log_config['handlers']['file']['filename'] = app_log_config['logger_file']
    set_log_config['loggers']['base_logger']['level'] = app_log_config['level']
    set_log_config['loggers']['base_logger']['handlers'] = app_log_config['handlers']
    setup_logging(set_log_config)
