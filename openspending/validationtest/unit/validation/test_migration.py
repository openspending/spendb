from ... import TestCase, helpers as h

from openspending.validation.model.migration import migrate_model
from openspending.validation.model import validate_model
from openspending.validation.model.migration import \
    m2011_11_20_require_name_attribute, \
    m2011_11_21_normalize_types, \
    m2011_11_22_unique_keys, \
    m2011_12_07_attributes_dictionary


class TestMigration(TestCase):

    def test_sanity_check(self):
        model = migrate_model(h.model_fixture('default'))
        # this should not raise!
        validate_model(model)

    def test_2011_11_20_require_name_attribute(self):
        model = h.model_fixture('2011_11_20_name_attribute')
        assert len(model['mapping']['function']['fields'])==2
        out = m2011_11_20_require_name_attribute(model)
        assert len(out['mapping']['function']['fields'])==3
        names = map(lambda f: f['name'], out['mapping']['function']['fields'])
        assert 'name' in names, names

    def test_2011_11_21_normalize_types(self):
        model = h.model_fixture('2011_11_21_normalize')
        out = m2011_11_21_normalize_types(model)
        assert out['mapping']['time']['type']=='date', out
        assert out['mapping']['transaction_id']['type']=='attribute', out
        assert out['mapping']['function']['type']=='compound', out

    def test_2011_11_22_unique_keys(self):
        model = h.model_fixture('2011_11_22_unique_keys')
        out = m2011_11_22_unique_keys(model)
        assert not 'unique_keys' in out['dataset']
        assert not 'key' in out['mapping']['supplier']
        assert out['mapping']['function']['key']

    def test_2011_12_07_attribute_dicts(self):
        model = h.model_fixture('2011_12_07_attribute_dicts')
        out =  m2011_12_07_attributes_dictionary(model)
        assert not 'fields' in out['mapping']['function']
        assert 'attributes' in out['mapping']['function']
        assert 'datatype' in out['mapping']['function']['attributes']['name']
        assert 'id'==out['mapping']['function']['attributes']['name']['datatype']


