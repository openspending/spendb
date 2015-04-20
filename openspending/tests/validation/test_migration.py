from openspending.validation.migration import migrate_model
from openspending.validation.model import validate_model

from openspending.tests.base import TestCase
from openspending.tests.helpers import validation_fixture


class TestMigration(TestCase):

    def test_sanity_check(self):
        model = migrate_model(validation_fixture('default'))
        # this should not raise!
        validate_model(model)
