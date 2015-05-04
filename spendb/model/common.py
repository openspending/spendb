# coding=utf-8
import datetime
import json

import colander
import sqlalchemy as sqla
from sqlalchemy.ext import mutable


def json_default(obj):
    if isinstance(obj, datetime.datetime):
        obj = obj.date()
    if isinstance(obj, datetime.date):
        obj = obj.isoformat()
    return obj


class Ref(object):

    def deserialize(self, node, cstruct):
        if cstruct is colander.null:
            return colander.null
        value = self.decode(cstruct)
        if value is None:
            raise colander.Invalid(node, 'Missing')
        return value

    def cstruct_children(self, node, cstruct):
        return []


class JSONType(sqla.TypeDecorator):
    """Enables JSON storage by encoding and decoding on the fly."""
    impl = sqla.Unicode

    def process_bind_param(self, value, dialect):
        return json.dumps(value, default=json_default)

    def process_result_value(self, value, dialect):
        return json.loads(value)

mutable.MutableDict.associate_with(JSONType)
