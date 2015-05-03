# coding=utf-8
import datetime
from json import dumps, loads

import colander
from sqlalchemy.types import Text, TypeDecorator
from sqlalchemy.sql.expression import select, func
from sqlalchemy.ext.mutable import Mutable

from spendb.core import db


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


class MutableDict(Mutable, dict):

    """
    Create a mutable dictionary to track mutable values
    and notify listeners upon change.
    """

    @classmethod
    def coerce(cls, key, value):
        """
        Convert plain dictionaries to MutableDict
        """

        # If it isn't a MutableDict already we conver it
        if not isinstance(value, MutableDict):
            # If it is a dictionary we can convert it
            if isinstance(value, dict):
                return MutableDict(value)

            # Try to coerce but it will probably return a ValueError
            return Mutable.coerce(key, value)
        else:
            # Since we already have a MutableDict we can just return it
            return value

    def __setitem__(self, key, value):
        """
        Set a value to a key and notify listeners of change
        """

        dict.__setitem__(self, key, value)
        self.changed()

    def __delitem__(self, key):
        """
        Delete a key and notify listeners of change
        """

        dict.__delitem__(self, key)
        self.changed()


class JSONType(TypeDecorator):
    impl = Text

    def __init__(self):
        super(JSONType, self).__init__()

    def process_bind_param(self, value, dialect):
        return dumps(value, default=json_default)

    def process_result_value(self, value, dialiect):
        return loads(value)

    def copy_value(self, value):
        return loads(dumps(value))


class DatasetFacetMixin(object):

    @classmethod
    def dataset_counts(cls, datasets_q):
        sq = datasets_q.subquery()
        q = select([cls.code, func.count(cls.dataset_id)],
                   group_by=cls.code,
                   order_by=func.count(cls.dataset_id).desc())
        q = q.where(cls.dataset_id == sq.c.id)
        return db.session.bind.execute(q).fetchall()
