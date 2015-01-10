from sqlalchemy import Integer, UnicodeText, Float, Unicode
from nose.tools import assert_raises

from openspending.tests.helpers import model_fixture, load_fixture
from openspending.tests.base import DatabaseTestCase

from openspending.core import db
from openspending.model.dataset import Dataset
from openspending.model import analytics
from openspending.model.dimension import (AttributeDimension, Measure,
                                          CompoundDimension, DateDimension)


class TestDataset(DatabaseTestCase):

    def setUp(self):
        super(TestDataset, self).setUp()
        self.ds = load_fixture('simple')

    def test_load_model_properties(self):
        assert self.ds.name == self.model['dataset']['name'], self.ds.name
        assert self.ds.label == self.model['dataset']['label'], self.ds.label

    def test_load_model_dimensions(self):
        assert len(self.ds.model.dimensions) == 4, self.ds.model.dimensions
        assert isinstance(self.ds.model['time'], DateDimension), \
            self.ds.model['time']
        assert isinstance(
            self.ds.model['field'], AttributeDimension), self.ds.model['field']
        assert isinstance(self.ds.model['to'], CompoundDimension), \
            self.ds.model['to']
        assert isinstance(self.ds.model['function'], CompoundDimension), \
            self.ds.model['function']
        assert len(self.ds.model.measures) == 1, self.ds.model.measures
        assert isinstance(self.ds.model['amount'], Measure), \
            self.ds.model['amount']

    def test_generate_db_entry_table(self):
        assert self.ds.fact_table.table.name == 'test__facts', \
            self.ds.fact_table.table.name
        cols = self.ds.fact_table.table.c
        assert '_id' in cols, cols
        assert isinstance(cols['_id'].type, Unicode)
        assert 'year' in cols, cols
        assert isinstance(cols['year'].type, Integer)
        assert 'amount' in cols
        assert isinstance(cols['amount'].type, Integer)
        assert 'field' in cols
        assert isinstance(cols['field'].type, Unicode)
        assert 'to_label' in cols, cols
        assert isinstance(cols['to_label'].type, Unicode)
        assert 'func_label' in cols
        assert isinstance(cols['func_label'].type, Unicode)
        assert_raises(KeyError, cols.__getitem__, 'foo')

    def test_facet_dimensions(self):
        assert [d.name for d in self.ds.model.facet_dimensions] == ['to']


class TestDatasetLoad(DatabaseTestCase):

    def setUp(self):
        super(TestDatasetLoad, self).setUp()
        self.ds = load_fixture('simple')
        self.engine = db.engine

    def test_load_all(self):
        q = self.ds.fact_table.table.select()
        resn = self.engine.execute(q).fetchall()
        assert len(resn) == 6, resn
        row0 = dict(resn[0].items())
        assert row0['amount'] == 200, row0.items()
        assert row0['field'] == 'foo', row0.items()

    def test_drop(self):
        tn = self.engine.table_names()
        assert 'test__facts' in tn, tn

        self.ds.fact_table.drop()
        tn = self.engine.table_names()
        assert 'test__facts' not in tn, tn

    def test_dataset_count(self):
        assert self.ds.fact_table.num_entries() == 6, \
            self.ds.fact_table.num_entries()

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

    def test_materialize_table(self):
        itr = self.ds.fact_table.entries()
        tbl = list(itr)
        assert len(tbl) == 6, len(tbl)
        row = tbl[0]
        assert isinstance(row['field'], unicode), row
        assert isinstance(row['function'], dict), row
        assert isinstance(row['to'], dict), row
