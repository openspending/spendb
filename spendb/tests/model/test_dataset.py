from sqlalchemy import Integer, Unicode
from nose.tools import assert_raises
from babbage.model import Dimension, Measure

from spendb.tests.helpers import load_fixture
from spendb.tests.base import DatabaseTestCase

from spendb.core import db


class TestDataset(DatabaseTestCase):

    def setUp(self):
        super(TestDataset, self).setUp()
        self.ds = load_fixture('simple')

    def test_load_model_properties(self):
        assert self.ds.name == self.ds.to_dict()['name'], self.ds.name
        assert self.ds.label == self.ds.to_dict()['label'], self.ds.label

    def test_load_model_dimensions(self):
        dims = {d.name: d for d in self.ds.model.dimensions}
        assert len(dims) == 4, dims
        assert isinstance(dims['time'], Dimension), dims['time']
        assert isinstance(dims['field'], Dimension), dims['field']
        assert isinstance(dims['to'], Dimension), dims['to']
        assert isinstance(dims['function'], Dimension), dims['function']
        meas = {m.name: m for m in self.ds.model.measures}
        assert len(meas) == 1, meas
        assert isinstance(meas['amount'], Measure), meas['amount']

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
        q = self.ds.fact_table.table.select()
        resn = self.engine.execute(q).fetchall()
        assert len(resn) == 6, resn
