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
        ms['dimensions']['from'] = ms['dimensions']['cofinance']
        validate_model(ms)

    @raises(Invalid)
    def test_to_is_compound(self):
        ms = self.model['model']
        ms['dimensions']['to'] = ms['dimensions']['transaction_id']
        validate_model(ms)

    @raises(Invalid)
    def test_invalid_name(self):
        ms = self.model['model']
        ms['dimensions']['ba nana'] = ms['dimensions']['function']
        validate_model(ms)

    @raises(Invalid)
    def test_no_label(self):
        ms = self.model['model'].copy()
        del ms['dimensions']['function']['label']
        validate_model(ms)

    @raises(Invalid)
    def test_requires_time(self):
        ms = self.model['model'].copy()
        del ms['dimensions']['time']
        validate_model(ms)

    @raises(Invalid)
    def test_id_overlap(self):
        ms = self.model['model'].copy()
        ms['dimensions']['function_id'] = ms['dimensions']['function']
        model = self.model.copy()
        model['model'] = ms
        validate_model(ms)

    @raises(Invalid)
    def test_entry_overlap(self):
        ms = self.model['model'].copy()
        ms['dimensions']['entry_id'] = ms['dimensions']['function']
        model = self.model.copy()
        model['model'] = ms
        validate_model(ms)

    @raises(Invalid)
    def test_measure_has_column(self):
        ms = self.model['model'].copy()
        del ms['measures']['cofinance']['column']
        validate_model(ms)

    @raises(Invalid)
    def test_measure_data_type(self):
        ms = self.model['model'].copy()
        ms['dimensions']['cofinance']['datatype'] = 'id'
        validate_model(ms)

    @raises(Invalid)
    def test_date_has_column(self):
        ms = self.model['model'].copy()
        del ms['dimensions']['time']['column']
        validate_model(ms)

    @raises(Invalid)
    def test_date_data_type(self):
        ms = self.model['model'].copy()
        ms['dimensions']['time']['datatype'] = 'id'
        validate_model(ms)

    @raises(Invalid)
    def test_compound_has_fields(self):
        ms = self.model['model'].copy()
        del ms['dimensions']['function']['attributes']
        validate_model(ms)

    @raises(Invalid)
    def test_compound_field_has_name(self):
        ms = self.model['model'].copy()
        del ms['dimensions']['function']['attributes']['name']
        validate_model(ms)

    @raises(Invalid)
    def test_compound_field_reserved_name(self):
        ms = self.model['model'].copy()
        ms['dimensions']['function']['attributes']['id'] = \
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
    def test_compound_field_has_datatype(self):
        ms = self.model['model'].copy()
        del ms['dimensions']['function']['attributes']['description']['type']
        validate_model(ms)

    @raises(Invalid)
    def test_compound_field_invalid_datatype(self):
        ms = self.model['model'].copy()
        ms['dimensions']['function']['attributes']['description']['type'] = 'banana'
        validate_model(ms)

    @raises(Invalid)
    def test_compound_field_name_not_datatype_id(self):
        ms = self.model['model'].copy()
        ms['dimensions']['function']['attributes']['name']['type'] = 'string'
        validate_model(ms)

    @raises(Invalid)
    def test_compound_must_have_name(self):
        ms = self.model['model'].copy()
        del ms['dimensions']['function']['attributes']['name']
        validate_model(ms)

    @raises(Invalid)
    def test_compound_must_have_label(self):
        ms = self.model['model'].copy()
        del ms['dimensions']['function']['attributes']['label']
        validate_model(ms)
