from colander import Invalid
from nose.tools import raises

from spendb.validation.dataset import validate_dataset

from spendb.tests.base import TestCase
from spendb.tests.helpers import validation_fixture


class TestDataset(TestCase):

    def setUp(self):
        super(TestDataset, self).setUp()
        self.model = validation_fixture('default')

    def test_basic_validate(self):
        try:
            ds = self.model['dataset']
            out = validate_dataset(ds)
            assert sorted(out.keys()) == sorted(ds.keys()), [out, ds]
        except Invalid, i:
            assert False, i.asdict()

    @raises(Invalid)
    def test_underscore_validate(self):
        ds = self.model['dataset'].copy()
        ds['name'] = 'test__'
        validate_dataset(ds)

    @raises(Invalid)
    def test_reserved_name_validate(self):
        ds = self.model['dataset'].copy()
        ds['name'] = 'entRY'
        validate_dataset(ds)

    @raises(Invalid)
    def test_invalid_currency(self):
        ds = self.model['dataset'].copy()
        ds['currency'] = 'glass pearls'
        validate_dataset(ds)

    @raises(Invalid)
    def test_invalid_category(self):
        ds = self.model['dataset'].copy()
        ds['category'] = 'giraffes'
        validate_dataset(ds)

    @raises(Invalid)
    def test_invalid_language(self):
        ds = self.model['dataset'].copy()
        ds['languages'].append('esperanto')
        validate_dataset(ds)

    @raises(Invalid)
    def test_invalid_country(self):
        ds = self.model['dataset'].copy()
        ds['territories'].append('SU')
        validate_dataset(ds)

    @raises(Invalid)
    def test_no_label(self):
        ds = self.model['dataset'].copy()
        del ds['label']
        validate_dataset(ds)

    @raises(Invalid)
    def test_empty_label(self):
        ds = self.model['dataset'].copy()
        ds['label'] = '   '
        validate_dataset(ds)

    def test_no_description(self):
        ds = self.model['dataset'].copy()
        del ds['description']
        validate_dataset(ds)
