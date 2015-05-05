from datetime import datetime
from sqlalchemy.orm import reconstructor, relationship, backref
from sqlalchemy.schema import Column, ForeignKey
from sqlalchemy.types import Integer, Unicode, Boolean, DateTime
from sqlalchemy.sql.expression import false, or_
from sqlalchemy.ext.associationproxy import association_proxy

from spendb.core import db, url_for
from spendb.model.model import Model
from spendb.model.fact_table import FactTable
from spendb.model.common import JSONType


class Dataset(db.Model):
    """ The dataset is the core entity of any access to data.
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
    category = Column(Unicode())
    private = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow,
                        onupdate=datetime.utcnow)
    data = Column(JSONType)

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
        return self.data.get('model', {})

    @property
    def fields(self):
        return self.data.get('fields', {})

    @fields.setter
    def fields(self, value):
        self.data['fields'] = value

    @property
    def samples(self):
        return self.data.get('samples', {})

    @samples.setter
    def samples(self, value):
        self.data['samples'] = value

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
            'currency': self.currency,
            'category': self.category,
            'private': self.private,
            'created_at': self.created_at,
            'updated_at': self.updated_at,
            'languages': list(self.languages),
            'territories': list(self.territories),
            'api_url': url_for('datasets_api.view', name=self.name)
        }

    def to_full_dict(self):
        full = self.data.copy()
        full['dataset'] = self.to_dict()
        return full

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
