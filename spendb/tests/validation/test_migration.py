from spendb.validation.migration import migrate_model
from spendb.validation.model import validate_model

from spendb.tests.base import TestCase
from spendb.tests.helpers import validation_fixture


class TestMigration(TestCase):

    def test_sanity_check(self):
        model = migrate_model(validation_fixture('default'))
        # this should not raise!
        validate_model(model)
