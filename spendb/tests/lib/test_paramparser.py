from openspending.lib.paramparser import ParamParser

from openspending.tests.base import TestCase


class TestParamParser(TestCase):

    def test_defaults(self):
        out, err = ParamParser({}).parse()
        assert out['page'] == 1
        assert out['pagesize'] == 10000
        assert out['order'] == []

    def test_page(self):
        out, err = ParamParser({'page': 'foo'}).parse()
        assert len(err) == 1
        assert '"page" has to be a number' in err[0]

    def test_page_fractional(self):
        out, err = ParamParser({'page': '1.2'}).parse()
        assert out['page'] == 1.2

        out, err = ParamParser({'page': '0.2'}).parse()
        assert out['page'] == 1

    def test_pagesize(self):
        out, err = ParamParser({'pagesize': 'foo'}).parse()
        assert len(err) == 1
        assert '"pagesize" has to be an integer' in err[0]

    def test_order(self):
        out, err = ParamParser({'order': 'foo:asc|amount:desc'}).parse()
        assert out['order'] == [('foo', False), ('amount', True)]

        out, err = ParamParser({'order': 'foo'}).parse()
        assert 'Wrong format for "order"' in err[0]

        out, err = ParamParser({'order': 'foo:boop'}).parse()
        assert 'Order direction can be "asc" or "desc"' in err[0]
