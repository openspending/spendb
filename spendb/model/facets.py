from datetime import datetime

from sqlalchemy.sql.expression import select, func

from spendb.core import db


class DatasetFacetMixin(object):

    @classmethod
    def dataset_counts(cls, datasets_q):
        sq = datasets_q.subquery()
        q = select([cls.code, func.count(cls.dataset_id)],
                   group_by=cls.code,
                   order_by=func.count(cls.dataset_id).desc())
        q = q.where(cls.dataset_id == sq.c.id)
        return db.session.bind.execute(q).fetchall()


class DatasetLanguage(db.Model, DatasetFacetMixin):
    __tablename__ = 'dataset_language'

    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.Unicode)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, onupdate=datetime.utcnow)

    dataset_id = db.Column(db.Integer, db.ForeignKey('dataset.id'))
    dataset = db.relationship('Dataset', backref=db.backref('_languages',
                                                            lazy=False))

    def __init__(self, code):
        self.code = code


class DatasetTerritory(db.Model, DatasetFacetMixin):
    __tablename__ = 'dataset_territory'

    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.Unicode)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, onupdate=datetime.utcnow)

    dataset_id = db.Column(db.Integer, db.ForeignKey('dataset.id'))
    dataset = db.relationship('Dataset', backref=db.backref('_territories',
                                                            lazy=False))

    def __init__(self, code):
        self.code = code
