from openspending.lib.paramparser import (ParamParser, AggregateParamParser)

from openspending.tests.base import TestCase
from mock import Mock, patch


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


class TestAggregateParamParser(TestCase):

    def test_defaults(self):
        out, err = AggregateParamParser({}).parse()
        assert out['page'] == 1
        assert out['pagesize'] == 10000
        assert err[0] == 'dataset name not provided'

    @patch('openspending.lib.paramparser.Dataset')
    def test_dataset(self, model_mock):
        ds = Mock()
        ds.model = Mock()
        ds.model.measures = []
        model_mock.by_name.return_value = ds

        out, err = AggregateParamParser({'dataset': 'foo'}).parse()
        assert out['dataset'] == ds

    def test_drilldown(self):
        out, err = AggregateParamParser({'drilldown': 'foo|bar|baz'}).parse()
        assert out['drilldown'] == ['foo', 'bar', 'baz']

    def test_format(self):
        out, err = AggregateParamParser({'format': 'json'}).parse()
        assert out['format'] == 'json'

        out, err = AggregateParamParser({'format': 'csv'}).parse()
        assert out['format'] == 'csv'

        out, err = AggregateParamParser({'format': 'html'}).parse()
        assert out['format'] == 'json'

    @patch('openspending.lib.paramparser.Dataset')
    def test_cut(self, model_mock):
        ds = Mock()
        ds.model = Mock()
        ds.model.measures = []
        model_mock.by_name.return_value = ds

        out, err = AggregateParamParser(
            {'dataset': 'foo', 'cut': 'foo:one|bar:two'}).parse()
        assert out['cut'] == [('foo', 'one'), ('bar', 'two')]

        out, err = AggregateParamParser(
            {'dataset': 'foo', 'cut': 'foo:one|bar'}).parse()
        assert 'Wrong format for "cut"' in err[0]

    @patch('openspending.lib.paramparser.Dataset')
    def test_measure(self, model_mock):
        ds = Mock()
        ds.model = Mock()
        amt = Mock()
        amt.name = 'amount'
        bar = Mock()
        bar.name = 'bar'
        ds.model.measures = [amt, bar]
        model_mock.by_name.return_value = ds

        out, err = AggregateParamParser({'dataset': 'foo'}).parse()
        assert out['measure'] == ['amount']

        out, err = AggregateParamParser(
            {'dataset': 'foo', 'measure': 'bar'}).parse()
        assert out['measure'] == ['bar']

        out, err = AggregateParamParser(
            {'dataset': 'foo', 'measure': 'amount|bar'}).parse()
        assert 'amount' in out['measure'], \
            "AggregateParamParser doesn't return amount measure"
        assert 'bar' in out['measure'], \
            "AggregateParamParser doesn't return bar measure"

        out, err = AggregateParamParser(
            {'dataset': 'foo', 'measure': 'baz'}).parse()
        assert 'no measure with name "baz"' in err[0]
