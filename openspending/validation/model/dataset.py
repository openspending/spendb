from openspending.validation.model.common import mapping
from openspending.validation.model.common import key, sequence
from openspending.validation.model.predicates import chained, \
        reserved_name, database_name, nonempty_string
from openspending.reference.currency import CURRENCIES
from openspending.reference.language import LANGUAGES
from openspending.reference.country import COUNTRIES
from openspending.reference.category import CATEGORIES


def no_double_underscore(name):
    """ Double underscores are used for dataset bunkering in the
    application, may not occur in the dataset name. """
    if '__' in name:
        return "Double underscores are not allowed in dataset names."
    return True


def valid_currency(code):
    if code.upper() not in CURRENCIES:
        return "%s is not a valid currency code." % code
    return True


def valid_category(cat):
    if cat.lower() not in CATEGORIES:
        return "%s is not a valid category." % cat
    return True


def valid_language(code):
    if code.lower() not in LANGUAGES:
        return "%s is not a valid language code." % code
    return True


def valid_country(code):
    if code.upper() not in COUNTRIES:
        return "%s is not a valid country code." % code
    return True


def dataset_schema(state):
    schema = mapping('dataset')
    schema.add(key('name', validator=chained(
            nonempty_string,
            reserved_name,
            database_name,
            no_double_underscore
        ),
        preparer=lambda x: x.lower().strip() if x else None))
    schema.add(key('currency', validator=chained(
            valid_currency
        )))
    schema.add(key('category', validator=chained(
            valid_category
        )))
    schema.add(key('label', validator=chained(
            nonempty_string,
        )))
    schema.add(key('description', validator=chained(
            nonempty_string,
        )))
    schema.add(sequence('languages',
        key('language', validator=valid_language), 
        missing=[]))
    schema.add(sequence('territories',
        key('territory', validator=valid_country), 
        missing=[]))
    return schema
