from datetime import datetime
from sqlalchemy.orm import reconstructor, relationship, backref
from sqlalchemy.schema import Column, ForeignKey
from sqlalchemy.types import Integer, Unicode, Boolean, DateTime
from sqlalchemy.sql.expression import false, or_
from sqlalchemy.ext.associationproxy import association_proxy

from spendb.core import db

from spendb.model.model import Model
from spendb.model.fact_table import FactTable
from spendb.model.common import (MutableDict, JSONType,
                                 DatasetFacetMixin)


class Dataset(db.Model):

    """ The dataset is the core entity of any access to data. All
    requests to the actual data store are routed through it, as well
    as data loading and model generation.

    The dataset keeps an in-memory representation of the data model
    (including all dimensions and measures) which can be used to
    generate necessary queries.
    """
    __tablename__ = 'dataset'

    id = Column(Integer, primary_key=True)
    name = Column(Unicode(255), unique=True)
    label = Column(Unicode(2000))
    description = Column(Unicode())
    currency = Column(Unicode())
    default_time = Column(Unicode())
    schema_version = Column(Unicode())
    category = Column(Unicode())
    private = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow,
                        onupdate=datetime.utcnow)
    data = Column(MutableDict.as_mutable(JSONType), default=dict)

    languages = association_proxy('_languages', 'code')
    territories = association_proxy('_territories', 'code')

    def __init__(self, data):
        self.data = data.copy()
        dataset = self.data['dataset']
        del self.data['dataset']
        self.update(dataset)
        self._load_model()

    def update(self, dataset):
        self.label = dataset.get('label')
        self.name = dataset.get('name')
        self.private = dataset.get('private')
        self.description = dataset.get('description')
        self.currency = dataset.get('currency')
        self.category = dataset.get('category')
        self.default_time = dataset.get('default_time')
        self.languages = dataset.get('languages', [])
        self.territories = dataset.get('territories', [])

    @property
    def model_data(self):
        model = self.data.copy()
        model['dataset'] = self.to_dict()
        return model

    @property
    def mapping(self):
        return self.data.get('mapping', {})

    @property
    def fields(self):
        return self.data.get('fields', {})

    @fields.setter
    def fields(self, value):
        self.data['fields'] = value

    @reconstructor
    def _load_model(self):
        self.model = Model(self)
        self.fact_table = FactTable(self)

    def touch(self):
        """ Update the dataset timestamp. This is used for cache
        invalidation. """
        self.updated_at = datetime.utcnow()
        db.session.add(self)

    def __repr__(self):
        return "<Dataset(%r,%r)>" % (self.id, self.name)

    def to_dict(self):
        return {
            'label': self.label,
            'name': self.name,
            'description': self.description,
            'default_time': self.default_time,
            'schema_version': self.schema_version,
            'currency': self.currency,
            'category': self.category,
            'timestamps': {
                'created': self.created_at,
                'last_modified': self.updated_at
            },
            'languages': list(self.languages),
            'territories': list(self.territories)
        }

    @classmethod
    def all_by_account(cls, account, order=True):
        """ Query available datasets based on dataset visibility. """
        from spendb.model.account import Account
        criteria = [cls.private == false()]
        if isinstance(account, Account) and account.is_authenticated():
            criteria += ["1=1" if account.admin else "1=2",
                         cls.managers.any(Account.id == account.id)]
        q = db.session.query(cls).filter(or_(*criteria))
        if order:
            q = q.order_by(cls.label.asc())
        return q

    @classmethod
    def by_name(cls, name):
        return db.session.query(cls).filter_by(name=name).first()


class DatasetLanguage(db.Model, DatasetFacetMixin):
    __tablename__ = 'dataset_language'

    id = Column(Integer, primary_key=True)
    code = Column(Unicode)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, onupdate=datetime.utcnow)

    dataset_id = Column(Integer, ForeignKey('dataset.id'))
    dataset = relationship(Dataset, backref=backref('_languages', lazy=False))

    def __init__(self, code):
        self.code = code


class DatasetTerritory(db.Model, DatasetFacetMixin):
    __tablename__ = 'dataset_territory'

    id = Column(Integer, primary_key=True)
    code = Column(Unicode)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, onupdate=datetime.utcnow)

    dataset_id = Column(Integer, ForeignKey('dataset.id'))
    dataset = relationship(Dataset, backref=backref('_territories',
                                                    lazy=False))

    def __init__(self, code):
        self.code = code
