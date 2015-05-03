from datetime import datetime

from sqlalchemy.orm import relationship, backref
from sqlalchemy.schema import Column, ForeignKey
from sqlalchemy.types import Integer, Unicode, DateTime

from spendb.core import db, url_for
from spendb.model.dataset import Dataset


class Run(db.Model):
    """ A run is a generic grouping object for background operations
    that perform logging to the frontend. """
    __tablename__ = 'run'

    # Status values
    STATUS_RUNNING = 'running'
    STATUS_COMPLETE = 'complete'
    STATUS_FAILED = 'failed'

    id = Column(Integer, primary_key=True)
    operation = Column(Unicode())
    status = Column(Unicode())
    source = Column(Unicode())
    time_start = Column(DateTime, default=datetime.utcnow)
    time_end = Column(DateTime)

    dataset_id = Column(Integer, ForeignKey('dataset.id'), nullable=True)
    dataset = relationship(Dataset,
                           backref=backref('runs',
                                           order_by='Run.time_start.desc()',
                                           lazy='dynamic'))

    def __init__(self, operation, status, dataset):
        self.operation = operation
        self.status = status
        self.dataset = dataset

    def to_dict(self):
        return {
            'id': self.id,
            'api_url': url_for('runs_api.view', dataset=self.dataset.name,
                               id=self.id),
            'operation': self.operation,
            'status': self.status,
            'source': self.source,
            'time_start': self.time_start,
            'time_end': self.time_end
        }

    @classmethod
    def all(cls, dataset):
        q = db.session.query(cls).filter_by(dataset=dataset)
        return q.order_by(cls.time_start.asc())

    @classmethod
    def by_id(cls, dataset, id):
        return cls.all(dataset).filter_by(id=id).first()

    def __repr__(self):
        return "<Run(%r, %r, %r)>" % (self.source, self.id, self.status)
