from datetime import datetime
from sqlalchemy.orm import reconstructor
from sqlalchemy.schema import Column
from sqlalchemy.types import Integer, Unicode, Boolean, DateTime
from sqlalchemy.sql.expression import or_
from sqlalchemy.ext.associationproxy import association_proxy

from spendb.core import db, url_for
from spendb.model.model import Model
from spendb.model.fact_table import FactTable
from spendb.model.common import JSONType


class Dataset(db.Model):
    """ The dataset is the core entity of any access to data.
    The dataset keeps an in-memory representation of the data model
    (including all dimensions and measures) which can be used to
    generate necessary queries. """
    __tablename__ = 'dataset'

    id = Column(Integer, primary_key=True)
    name = Column(Unicode(255), unique=True)
    label = Column(Unicode(2000))
    description = Column(Unicode())
    currency = Column(Unicode())
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
        self.name = dataset.get('name')
        self.update(dataset)
        self._load_model()

    def update(self, dataset):
        self.label = dataset.get('label')
        if 'private' in dataset:
            self.private = dataset.get('private')
        if 'description' in dataset:
            self.description = dataset.get('description')
        if 'currency' in dataset:
            self.currency = dataset.get('currency')
        if 'category' in dataset:
            self.category = dataset.get('category')
        if 'languages' in dataset:
            self.languages = dataset.get('languages', [])
        if 'territories' in dataset:
            self.territories = dataset.get('territories', [])

    @property
    def model_data(self):
        return self.data.get('model', {})

    @property
    def has_model(self):
        model = self.model_data
        return 'measures' in model and 'dimensions' in model

    def update_model(self, model):
        self.data['model'] = model
        self._load_model()

        # TODO find a better place for this.
        for dimension in self.model.dimensions:
            dimension.data['cardinality'] = \
                self.fact_table.num_members(dimension)

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
            'currency': self.currency,
            'category': self.category,
            'private': self.private,
            'created_at': self.created_at,
            'updated_at': self.updated_at,
            'languages': list(self.languages),
            'territories': list(self.territories),
            'has_model': self.has_model,
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
        has_user = account and account.is_authenticated()
        has_admin = has_user and account.admin
        q = db.session.query(cls)
        if not has_admin:
            criteria = [cls.private == False]  # noqa
            if has_user:
                criteria.append(cls.managers.any(Account.id == account.id))
            q = q.filter(or_(*criteria))

        if order:
            q = q.order_by(cls.label.asc())
        return q

    @classmethod
    def by_name(cls, name):
        return db.session.query(cls).filter_by(name=name).first()
