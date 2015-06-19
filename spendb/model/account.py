import uuid
import hmac

from flask.ext.login import AnonymousUserMixin

from spendb.core import db, login_manager


def make_uuid():
    return unicode(uuid.uuid4())


account_dataset_table = db.Table(
    'account_dataset', db.metadata,
    db.Column('dataset_id', db.Integer, db.ForeignKey('dataset.id'),
              primary_key=True),
    db.Column('account_id', db.Integer, db.ForeignKey('account.id'),
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

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Unicode(255), unique=True)
    fullname = db.Column(db.Unicode(2000))
    email = db.Column(db.Unicode(2000))
    twitter_handle = db.Column(db.Unicode(140))
    public_email = db.Column(db.Boolean, default=False)
    public_twitter = db.Column(db.Boolean, default=False)
    password = db.Column(db.Unicode(2000))
    api_key = db.Column(db.Unicode(2000), default=make_uuid)
    admin = db.Column(db.Boolean, default=False)

    datasets = db.relationship('Dataset',
                               secondary=account_dataset_table,
                               backref=db.backref('managers', lazy='dynamic'))

    def __init__(self):
        self.api_key = make_uuid()

    def is_authenticated(self):
        return True

    def is_anonymous(self):
        return False

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
            'display_name': self.display_name,
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
