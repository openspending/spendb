from colander import Invalid
from nose.tools import raises

from spendb.validation.dataset import dataset_schema
from spendb.validation.common import ValidationState

from spendb.tests.base import TestCase
from spendb.tests.helpers import validation_fixture


class TestDataset(TestCase):

    def setUp(self):
        super(TestDataset, self).setUp()
        self.model = validation_fixture('default')
        self.state = ValidationState(self.model)

    def test_basic_validate(self):
        try:
            ds = self.model['dataset']
            schema = dataset_schema(self.state)
            out = schema.deserialize(ds)
            assert sorted(out.keys())==sorted(ds.keys()), [out, ds]
        except Invalid, i:
            assert False, i.asdict()

    @raises(Invalid)
    def test_underscore_validate(self):
        ds = self.model['dataset'].copy()
        ds['name'] = 'test__'
        schema = dataset_schema(self.state)
        schema.deserialize(ds)

    @raises(Invalid)
    def test_reserved_name_validate(self):
        ds = self.model['dataset'].copy()
        ds['name'] = 'entRY'
        schema = dataset_schema(self.state)
        schema.deserialize(ds)

    @raises(Invalid)
    def test_invalid_currency(self):
        ds = self.model['dataset'].copy()
        ds['currency'] = 'glass pearls'
        schema = dataset_schema(self.state)
        schema.deserialize(ds)

    @raises(Invalid)
    def test_invalid_category(self):
        ds = self.model['dataset'].copy()
        ds['category'] = 'giraffes'
        schema = dataset_schema(self.state)
        schema.deserialize(ds)

    @raises(Invalid)
    def test_invalid_language(self):
        ds = self.model['dataset'].copy()
        ds['languages'].append('esperanto')
        schema = dataset_schema(self.state)
        schema.deserialize(ds)

    @raises(Invalid)
    def test_invalid_country(self):
        ds = self.model['dataset'].copy()
        ds['territories'].append('SU')
        schema = dataset_schema(self.state)
        schema.deserialize(ds)

    @raises(Invalid)
    def test_no_label(self):
        ds = self.model['dataset'].copy()
        del ds['label']
        schema = dataset_schema(self.state)
        schema.deserialize(ds)

    @raises(Invalid)
    def test_empty_label(self):
        ds = self.model['dataset'].copy()
        ds['label'] = '  '
        schema = dataset_schema(self.state)
        schema.deserialize(ds)

    def test_no_description(self):
        ds = self.model['dataset'].copy()
        del ds['description']
        schema = dataset_schema(self.state)
        schema.deserialize(ds)
