from colander import Invalid
from nose.tools import raises

from spendb.validation.model import validate_model

from spendb.tests.base import TestCase
from spendb.tests.helpers import validation_fixture


class TestModel(TestCase):

    def setUp(self):
        super(TestModel, self).setUp()
        self.model = validation_fixture('default')

    def test_basic_validate(self):
        try:
            in_ = self.model['model']
            out = validate_model(in_)
            assert len(out) == len(in_), out
        except Invalid, i:
            assert False, i.asdict()

    @raises(Invalid)
    def test_from_is_compound(self):
        ms = self.model['model']
        ms['dimensions']['from'] = ms['measures']['cofinance']
        validate_model(ms)

    @raises(Invalid)
    def test_invalid_name(self):
        ms = self.model['model']
        ms['dimensions']['ba nana'] = ms['dimensions']['function']
        validate_model(ms)

    @raises(Invalid)
    def test_no_measures(self):
        ms = self.model['model']
        ms['measures'] = {}
        validate_model(ms)

    @raises(Invalid)
    def test_no_dimensions(self):
        ms = self.model['model']
        ms['dimensions'] = {}
        validate_model(ms)

    @raises(Invalid)
    def test_measure_has_column(self):
        ms = self.model['model'].copy()
        del ms['measures']['cofinance']['column']
        validate_model(ms)

    @raises(Invalid)
    def test_measure_data_type(self):
        ms = self.model['model'].copy()
        ms['measures']['cofinance']['type'] = 'string'
        validate_model(ms)

    @raises(Invalid)
    def test_date_has_column(self):
        ms = self.model['model'].copy()
        del ms['dimensions']['time']['attributes']['year']['column']
        validate_model(ms)

    @raises(Invalid)
    def test_compound_has_fields(self):
        ms = self.model['model'].copy()
        del ms['dimensions']['function']['attributes']
        validate_model(ms)

    @raises(Invalid)
    def test_compound_field_with_dash(self):
        ms = self.model['model'].copy()
        ms['dimensions']['function']['attributes']['id-col'] = \
            ms['dimensions']['function']['attributes']['description']
        del ms['dimensions']['function']['attributes']['description']
        validate_model(ms)

    @raises(Invalid)
    def test_compound_field_short(self):
        ms = self.model['model'].copy()
        ms['dimensions']['function']['attributes']['i'] = \
            ms['dimensions']['function']['attributes']['description']
        del ms['dimensions']['function']['attributes']['description']
        validate_model(ms)

    @raises(Invalid)
    def test_compound_field_long(self):
        ms = self.model['model'].copy()
        a = 'xxxxfdgjkdhgsjkfhglhdjghdfhlkgshlfdhjkhfdlkjhjklfdhljkgdfhlkjghjk'
        ms['dimensions']['function']['attributes'][a] = \
            ms['dimensions']['function']['attributes']['description']
        del ms['dimensions']['function']['attributes']['description']
        validate_model(ms)

    @raises(Invalid)
    def test_compound_field_invalid_name(self):
        ms = self.model['model'].copy()
        ms['dimensions']['function']['attributes']['ba nanana'] = \
            ms['dimensions']['function']['attributes']['description']
        del ms['dimensions']['function']['attributes']['description']
        validate_model(ms)

    @raises(Invalid)
    def test_compound_field_has_column(self):
        ms = self.model['model'].copy()
        del ms['dimensions']['function']['attributes']['description']['column']
        validate_model(ms)

    @raises(Invalid)
    def test_compound_field_invalid_type(self):
        ms = self.model['model'].copy()
        ms['dimensions']['function']['attributes']['description']['type'] = 'banana'
        validate_model(ms)
