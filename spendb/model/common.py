# coding=utf-8
import datetime
import json

import sqlalchemy as sqla
from sqlalchemy.ext import mutable


def json_default(obj):
    if isinstance(obj, datetime.datetime):
        obj = obj.date()
    if isinstance(obj, datetime.date):
        obj = obj.isoformat()
    return obj


class JSONType(sqla.TypeDecorator):
    """Enables JSON storage by encoding and decoding on the fly."""
    impl = sqla.Unicode

    def process_bind_param(self, value, dialect):
        return json.dumps(value, default=json_default)

    def process_result_value(self, value, dialect):
        return json.loads(value)

mutable.MutableDict.associate_with(JSONType)
