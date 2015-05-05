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
            in_ = self.model['mapping']
            out = validate_model(in_)
            assert len(out)==len(in_), out
        except Invalid, i:
            assert False, i.asdict()

    @raises(Invalid)
    def test_from_is_compound(self):
        ms = self.model['mapping']
        ms['dimensions']['from'] = ms['cofinance']
        validate_model(ms)

    @raises(Invalid)
    def test_to_is_compound(self):
        ms = self.model['mapping']
        ms['to'] = ms['transaction_id']
        validate_model(ms)

    @raises(Invalid)
    def test_invalid_name(self):
        ms = self.model['mapping']
        ms['ba nana'] = ms['function']
        validate_model(ms)

    @raises(Invalid)
    def test_no_label(self):
        ms = self.model['mapping'].copy()
        del ms['function']['label']
        validate_model(ms)

    @raises(Invalid)
    def test_requires_one_key_column(self):
        ms = self.model['mapping'].copy()
        del ms['function']['key']
        validate_model(ms)

    @raises(Invalid)
    def test_requires_time(self):
        ms = self.model['mapping'].copy()
        del ms['time']
        validate_model(ms)

    @raises(Invalid)
    def test_requires_time_date_datatype(self):
        ms = self.model['mapping'].copy()
        ms['time']['datatype'] = 'string'
        validate_model(ms)

    @raises(Invalid)
    def test_requires_amount(self):
        ms = self.model['mapping'].copy()
        del ms['amount']
        validate_model(ms)

    @raises(Invalid)
    def test_requires_amount_float_datatype(self):
        ms = self.model['mapping'].copy()
        ms['amount']['datatype'] = 'string'
        validate_model(ms)

    @raises(Invalid)
    def test_id_overlap(self):
        ms = self.model['mapping'].copy()
        ms['function_id'] = ms['function']
        model = self.model.copy()
        model['mapping'] = ms
        validate_model(ms)

    @raises(Invalid)
    def test_entry_overlap(self):
        ms = self.model['mapping'].copy()
        ms['entry_id'] = ms['function']
        model = self.model.copy()
        model['mapping'] = ms
        validate_model(ms)

    @raises(Invalid)
    def test_measure_has_column(self):
        ms = self.model['mapping'].copy()
        del ms['cofinance']['column']
        validate_model(ms)

    @raises(Invalid)
    def test_measure_data_type(self):
        ms = self.model['mapping'].copy()
        ms['cofinance']['datatype'] = 'id'
        validate_model(ms)

    @raises(Invalid)
    def test_date_has_column(self):
        ms = self.model['mapping'].copy()
        del ms['time']['column']
        validate_model(ms)

    @raises(Invalid)
    def test_date_data_type(self):
        ms = self.model['mapping'].copy()
        ms['time']['datatype'] = 'id'
        validate_model(ms)

    @raises(Invalid)
    def test_attribute_has_column(self):
        ms = self.model['mapping'].copy()
        del ms['transaction_id']['column']
        validate_model(ms)

    @raises(Invalid)
    def test_attribute_data_type(self):
        ms = self.model['mapping'].copy()
        ms['transaction_id']['datatype'] = 'banana'
        validate_model(ms)

    @raises(Invalid)
    def test_compound_has_fields(self):
        ms = self.model['mapping'].copy()
        del ms['function']['attributes']
        validate_model(ms)

    @raises(Invalid)
    def test_compound_field_has_name(self):
        ms = self.model['mapping'].copy()
        del ms['function']['attributes']['name']
        validate_model(ms)

    @raises(Invalid)
    def test_compound_field_reserved_name(self):
        ms = self.model['mapping'].copy()
        ms['function']['attributes']['id'] = ms['function']['attributes']['description']
        del ms['function']['attributes']['description']
        validate_model(ms)

    @raises(Invalid)
    def test_compound_field_invalid_name(self):
        ms = self.model['mapping'].copy()
        ms['function']['attributes']['ba nanana'] = ms['function']['attributes']['description']
        del ms['function']['attributes']['description']
        validate_model(ms)

    @raises(Invalid)
    def test_compound_field_has_column(self):
        ms = self.model['mapping'].copy()
        del ms['function']['attributes']['description']['column']
        validate_model(ms)

    @raises(Invalid)
    def test_compound_field_has_datatype(self):
        ms = self.model['mapping'].copy()
        del ms['function']['attributes']['description']['datatype']
        validate_model(ms)

    @raises(Invalid)
    def test_compound_field_invalid_datatype(self):
        ms = self.model['mapping'].copy()
        ms['function']['attributes']['description']['datatype'] = 'banana'
        validate_model(ms)

    @raises(Invalid)
    def test_compound_field_name_not_datatype_id(self):
        ms = self.model['mapping'].copy()
        ms['function']['attributes']['name']['datatype'] = 'string'
        validate_model(ms)

    @raises(Invalid)
    def test_compound_field_label_not_datatype_string(self):
        ms = self.model['mapping'].copy()
        ms['function']['attributes']['label']['datatype'] = 'float'
        validate_model(ms)

    @raises(Invalid)
    def test_compound_must_have_name(self):
        ms = self.model['mapping'].copy()
        del ms['function']['attributes']['name']
        validate_model(ms)

    @raises(Invalid)
    def test_compound_must_have_label(self):
        ms = self.model['mapping'].copy()
        del ms['function']['attributes']['label']
        validate_model(ms)
