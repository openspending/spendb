import datetime

from ... import TestCase, helpers as h
from openspending.validation.data import convert_types

class TestTypes(TestCase):

    def test_convert_types_value(self):
        mapping = {
                    "foo": {"column": "foo", 
                           "datatype": "string"}
                  }
        row = {"foo": "bar"}
        out = convert_types(mapping, row)
        assert isinstance(out, dict), out
        assert 'foo' in out, out
        assert out['foo']=='bar'

    def test_convert_types_compound(self):
        mapping = {
                    "foo": {"attributes": {
                        "name": {"column": "foo_name", 
                            "datatype": "string"},
                        "label": {"column": "foo_label", 
                            "datatype": "string"}
                        }
                    }
                  }
        row = {"foo_name": "bar", "foo_label": "qux"}
        out = convert_types(mapping, row)
        assert isinstance(out, dict), out
        assert 'foo' in out, out
        assert isinstance(out['foo'], dict), out
        assert out['foo']['name']=='bar'
        assert out['foo']['label']=='qux'

    def test_convert_types_casting(self):
        mapping = {
                    "foo": {"column": "foo", 
                           "datatype": "float"}
                  }
        row = {"foo": "5.0"}
        out = convert_types(mapping, row)
        assert isinstance(out, dict), out
        assert 'foo' in out, out
        assert out['foo']==5.0

    def test_convert_dates(self):
        mapping = {
                    "foo": {"column": "foo", 
                           "datatype": "date"}
                  }
        row = {"foo": "2010"}
        out = convert_types(mapping, row)
        assert out['foo']==datetime.date(2010, 1, 1)
    
        row = {"foo": "2010-02"}
        out = convert_types(mapping, row)
        assert out['foo']==datetime.date(2010, 2, 1)
        
        row = {"foo": "2010-02-03"}
        out = convert_types(mapping, row)
        assert out['foo']==datetime.date(2010, 2, 3)

        row = {"foo": "2010-02-03Z"}
        out = convert_types(mapping, row)
        assert out['foo']==datetime.date(2010, 2, 3)

    def test_convert_dates_custom_format(self):
        mapping = {
                    "foo": {"column": "foo",
                            "format": "%d.%m.%Y", 
                            "datatype": "date"}
                  }
        row = {"foo": "7.5.2010"}
        out = convert_types(mapping, row)
        assert out['foo']==datetime.date(2010, 5, 7)
