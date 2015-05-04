# coding=utf-8
import datetime
import json

import colander
import sqlalchemy as sqla
from sqlalchemy.sql.expression import select, func
from sqlalchemy.ext import mutable

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


class JSONType(sqla.TypeDecorator):
    """Enables JSON storage by encoding and decoding on the fly."""
    impl = sqla.Unicode

    def process_bind_param(self, value, dialect):
        return json.dumps(value, default=json_default)

    def process_result_value(self, value, dialect):
        return json.loads(value)

mutable.MutableDict.associate_with(JSONType)


class DatasetFacetMixin(object):

    @classmethod
    def dataset_counts(cls, datasets_q):
        sq = datasets_q.subquery()
        q = select([cls.code, func.count(cls.dataset_id)],
                   group_by=cls.code,
                   order_by=func.count(cls.dataset_id).desc())
        q = q.where(cls.dataset_id == sq.c.id)
        return db.session.bind.execute(q).fetchall()
