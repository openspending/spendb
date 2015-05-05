from spendb.tests.helpers import load_fixture
from spendb.tests.base import DatabaseTestCase

from spendb.core import db
from spendb.model.model import Dimension


class TestDimension(DatabaseTestCase):

    def setUp(self):
        super(TestDimension, self).setUp()
        self.engine = db.engine
        self.meta = db.metadata
        self.meta.bind = self.engine
        self.ds = load_fixture('cra')
        self.dims = list(self.ds.model.dimensions)
        print self.dims
        for d in self.dims:
            if d.name == 'from':
                self.entity = d

    def test_is_dimension(self):
        assert isinstance(self.dims[0], Dimension), self.dims

    def test_basic_properties(self):
        assert self.entity.name == 'from', self.entity.name

    def test_attributes_exist_on_object(self):
        attrs = list(self.entity.attributes)
        assert len(attrs) == 3, attrs
        names = [a.name for a in attrs]
        assert 'name' in names, names

    def test_members(self):
        members = list(self.ds.fact_table.dimension_members(self.entity))
        assert len(members) == 5
