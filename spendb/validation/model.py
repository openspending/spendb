from babbage.validation import validate_model as babbage_validate

from spendb.core import db


TYPES = {
    'string': db.Unicode,
    'integer': db.BigInteger,
    'boolean': db.Boolean,
    'number': db.Float,
    # FIXME: add proper support for dates
    # 'date': db.Date
    'date': db.Unicode
}


def validate_model(model):
    """ Apply model validation. """
    babbage_validate(model)
    return model
