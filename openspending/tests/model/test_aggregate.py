from openspending.tests.helpers import load_fixture
from openspending.tests.base import DatabaseTestCase

from openspending.core import db
from openspending.model import analytics


class TestAggregate(DatabaseTestCase):

    def setUp(self):
        super(TestAggregate, self).setUp()
        self.ds = load_fixture('simple')
        self.engine = db.engine

    def test_aggregate_simple(self):
        res = analytics.aggregate(self.ds)
        assert res['summary']['num_entries'] == 6, res
        assert res['summary']['amount'] == 2690.0, res

    def test_aggregate_basic_cut(self):
        res = analytics.aggregate(self.ds, cuts=[('field', u'foo')])
        assert res['summary']['num_entries'] == 3, res
        assert res['summary']['amount'] == 1000, res

    def test_aggregate_dimensions_drilldown(self):
        res = analytics.aggregate(self.ds, drilldowns=['function'])
        assert res['summary']['num_entries'] == 6, res
        assert res['summary']['amount'] == 2690, res
        assert len(res['drilldown']) == 2, res['drilldown']

    def test_aggregate_two_dimensions_drilldown(self):
        res = analytics.aggregate(self.ds, drilldowns=['function', 'field'])
        assert res['summary']['num_entries'] == 6, res
        assert res['summary']['amount'] == 2690, res
        assert len(res['drilldown']) == 5, res['drilldown']

    def test_aggregate_by_attribute(self):
        res = analytics.aggregate(self.ds, drilldowns=['function.label'])
        assert len(res['drilldown']) == 2, res['drilldown']

    def test_aggregate_two_attributes_same_dimension(self):
        res = analytics.aggregate(self.ds, drilldowns=['function.name',
                                                       'function.label'])
        assert len(res['drilldown']) == 2, res['drilldown']
