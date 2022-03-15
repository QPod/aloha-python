import json
from datetime import datetime

from pandas._libs.tslibs.nattype import NaTType
from pandas._libs.tslibs.timestamps import Timestamp


class ObjectWithDateTimeEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, NaTType):  # notice: NaTType is a subclass of datetime
            return None
        if isinstance(obj, Timestamp):
            return obj.timestamp()
        if isinstance(obj, datetime):
            return obj.timestamp()

        return json.JSONEncoder.default(self, obj)
