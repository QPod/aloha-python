import sys

from .api import v0, v1, v2
from .http import DefaultHandler404

for module in (v0, v1, v2):
    full_name = '{}.{}'.format(__package__, module.__name__.rsplit('.')[-1])
    sys.modules[full_name] = sys.modules[module.__name__]
