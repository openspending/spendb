import colander
import uuid
import hmac

from flask.ext.login import AnonymousUserMixin
from sqlalchemy.orm import relationship, backref
from sqlalchemy.schema import Table, Column, ForeignKey
from sqlalchemy.types import Integer, Unicode, Boolean

from spendb.core import db, login_manager, url_for
from spendb.model.dataset import Dataset
from spendb.model.common import Ref

REGISTER_NAME_RE = r"^[a-zA-Z0-9_\-]{3,255}$"


def make_uuid():
    return unicode(uuid.uuid4())


account_dataset_table = Table(
    'account_dataset', db.metadata,
    Column('dataset_id', Integer, ForeignKey('dataset.id'),
           primary_key=True),
    Column('account_id', Integer, ForeignKey('account.id'),
           primary_key=True)
)


class AnonymousAccount(AnonymousUserMixin):
    admin = False

    def __repr__(self):
        return '<AnonymousAccount()>'

login_manager.anonymous_user = AnonymousAccount


@login_manager.user_loader
def load_account(account_id):
    return Account.by_id(account_id)


class Account(db.Model):
    __tablename__ = 'account'

    id = Column(Integer, primary_key=True)
    name = Column(Unicode(255), unique=True)
    fullname = Column(Unicode(2000))
    email = Column(Unicode(2000))
    twitter_handle = Column(Unicode(140))
    public_email = Column(Boolean, default=False)
    public_twitter = Column(Boolean, default=False)
    password = Column(Unicode(2000))
    api_key = Column(Unicode(2000), default=make_uuid)
    admin = Column(Boolean, default=False)

    datasets = relationship(Dataset,
                            secondary=account_dataset_table,
                            backref=backref('managers', lazy='dynamic'))

    def __init__(self):
        self.api_key = make_uuid()

    def is_authenticated(self):
        return True

    def is_active(self):
        return True

    def get_id(self):
        return self.id

    @property
    def display_name(self):
        return self.fullname or self.name

    @property
    def token(self):
        h = hmac.new('')
        h.update(self.api_key)
        if self.password:
            h.update(self.password)
        return h.hexdigest()

    @classmethod
    def by_name(cls, name):
        return db.session.query(cls).filter_by(name=name).first()

    @classmethod
    def by_id(cls, id):
        return db.session.query(cls).filter_by(id=id).first()

    @classmethod
    def by_email(cls, email):
        return db.session.query(cls).filter_by(email=email).first()

    @classmethod
    def by_api_key(cls, api_key):
        return db.session.query(cls).filter_by(api_key=api_key).first()

    def to_dict(self):
        """ Return the dictionary representation of the account. """
        account_dict = {
            'name': self.name,
            'fullname': self.fullname,
            'email': self.email,
            'admin': self.admin,
            'twitter_handle': self.twitter_handle
        }
        if not self.public_email:
            account_dict.pop('email')
        if not self.public_twitter:
            account_dict.pop('twitter_handle')
        return account_dict

    def __repr__(self):
        return '<Account(%r,%r)>' % (self.id, self.name)


class AccountRef(Ref):

    def decode(self, cstruct):
        if isinstance(cstruct, basestring):
            return Account.by_name(cstruct)
        if isinstance(cstruct, dict):
            return self.decode(cstruct.get('name'))
        return None


class DatasetAccounts(colander.SequenceSchema):
    account = colander.SchemaNode(AccountRef())


class AccountRegister(colander.MappingSchema):
    name = colander.SchemaNode(colander.String(),
                               validator=colander.Regex(REGISTER_NAME_RE))
    fullname = colander.SchemaNode(colander.String())
    email = colander.SchemaNode(colander.String(),
                                validator=colander.Email())
    public_email = colander.SchemaNode(colander.Boolean(), missing=False)
    password1 = colander.SchemaNode(colander.String(),
                                    validator=colander.Length(min=4))
    password2 = colander.SchemaNode(colander.String(),
                                    validator=colander.Length(min=4))
    terms = colander.SchemaNode(colander.Bool())


class AccountSettings(colander.MappingSchema):
    fullname = colander.SchemaNode(colander.String())
    email = colander.SchemaNode(colander.String(),
                                validator=colander.Email())
    public_email = colander.SchemaNode(colander.Boolean(), missing=False)
    twitter = colander.SchemaNode(colander.String(), missing=None,
                                  validator=colander.Length(max=140))
    public_twitter = colander.SchemaNode(colander.Boolean(), missing=False)
    password1 = colander.SchemaNode(colander.String(),
                                    missing=None, default=None)
    password2 = colander.SchemaNode(colander.String(),
                                    missing=None, default=None)
