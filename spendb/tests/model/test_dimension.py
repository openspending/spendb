from nose.tools import assert_raises

from openspending.tests.helpers import load_fixture
from openspending.tests.base import DatabaseTestCase

from openspending.core import db
from openspending.model.dimension import CompoundDimension


class TestCompoundDimension(DatabaseTestCase):

    def setUp(self):
        super(TestCompoundDimension, self).setUp()
        self.engine = db.engine
        self.meta = db.metadata
        self.meta.bind = self.engine
        self.ds = load_fixture('cra')
        self.entity = self.ds.model['from']
        self.classifier = self.ds.model['cofog1']

    def test_is_compound(self):
        assert isinstance(self.entity, CompoundDimension), self.entity

    def test_basic_properties(self):
        assert self.entity.name == 'from', self.entity.name
        assert self.classifier.name == 'cofog1', self.classifier.name

    def test_attributes_exist_on_object(self):
        assert len(self.entity.attributes) == 3, self.entity.attributes
        assert_raises(KeyError, self.entity.__getitem__, 'field')
        assert self.entity['name'].name == 'name'

    def test_members(self):
        members = list(self.ds.fact_table.dimension_members(self.entity))
        assert len(members) == 5
