from .logger import get_logger
from ..settings import SETTINGS

LOG = get_logger(
    level=SETTINGS.config.get('deploy', {}).get('log_level', 10)  # 10 = logging.DEBUG
)
