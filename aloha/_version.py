from datetime import datetime

_now = datetime.now()
__version__ = '%s.%02d%02d.%02d%02d' % (_now.year, _now.month, _now.day, _now.hour, _now.minute)
