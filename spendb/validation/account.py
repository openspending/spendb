from colander import SchemaNode, SequenceSchema, Regex, String, Length
from colander import MappingSchema, Email, Boolean

from spendb.validation.common import Ref

REGISTER_NAME_RE = r"^[a-zA-Z0-9_\-]{3,255}$"


class AccountRef(Ref):

    def decode(self, cstruct):
        from spendb.model import Account
        if isinstance(cstruct, basestring):
            return Account.by_name(cstruct)
        if isinstance(cstruct, dict):
            return self.decode(cstruct.get('name'))
        return None


class DatasetAccounts(SequenceSchema):
    account = SchemaNode(AccountRef())


class AccountRegister(MappingSchema):
    name = SchemaNode(String(), validator=Regex(REGISTER_NAME_RE))
    fullname = SchemaNode(String())
    email = SchemaNode(String(), validator=Email())
    public_email = SchemaNode(Boolean(), missing=False)
    password1 = SchemaNode(String(), validator=Length(min=4))
    password2 = SchemaNode(String(), validator=Length(min=4))
    terms = SchemaNode(Boolean())


class AccountSettings(MappingSchema):
    fullname = SchemaNode(String())
    email = SchemaNode(String(), validator=Email())
    public_email = SchemaNode(Boolean(), missing=False)
    twitter = SchemaNode(String(), missing=None,
                         validator=Length(max=140))
    public_twitter = SchemaNode(Boolean(), missing=False)
    password1 = SchemaNode(String(), missing=None, default=None)
    password2 = SchemaNode(String(), missing=None, default=None)
