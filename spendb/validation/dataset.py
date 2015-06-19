from colander import Schema, SchemaNode, String, Boolean, SequenceSchema
from colander import OneOf, Length, drop
from fiscalmodel import CURRENCIES, LANGUAGES
from fiscalmodel import COUNTRIES, CATEGORIES

from spendb.validation.common import dataset_name, prepare_name
from spendb.validation.account import AccountRef


class DatasetLanguages(SequenceSchema):
    language = SchemaNode(String(), validator=OneOf(LANGUAGES.keys()))


class DatasetTerritories(SequenceSchema):
    territory = SchemaNode(String(), validator=OneOf(COUNTRIES.keys()))


class DatasetForm(Schema):
    label = SchemaNode(String(), preparer=prepare_name,
                       validator=Length(min=2))
    name = SchemaNode(String(), preparer=prepare_name,
                      validator=dataset_name)
    description = SchemaNode(String(), missing=drop)
    private = SchemaNode(Boolean(), missing=drop)
    currency = SchemaNode(String(), missing=drop,
                          validator=OneOf(CURRENCIES.keys()))
    category = SchemaNode(String(), missing=drop,
                          validator=OneOf(CATEGORIES.keys()))
    languages = DatasetLanguages(missing=drop)
    territories = DatasetTerritories(missing=drop)


class Managers(SequenceSchema):
    manager = SchemaNode(AccountRef())


class ManagersForm(Schema):
    managers = Managers(missing=[])


def validate_dataset(data):
    return DatasetForm().deserialize(data)


def validate_managers(data):
    return ManagersForm().deserialize(data)
