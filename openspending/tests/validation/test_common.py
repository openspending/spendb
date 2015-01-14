from openspending.validation.common import ValidationState

from openspending.tests.base import TestCase
from openspending.tests.helpers import validation_fixture


class TestValidationState(TestCase):

    def setUp(self):
        super(TestValidationState, self).setUp()
        self.state = ValidationState(validation_fixture('default'))

    def test_list_attributes(self):
        attributes = list(self.state.attributes)
        assert len(attributes) == 11, attributes
        assert 'amount' in attributes, attributes
        assert 'function.label' in attributes, attributes
        assert not 'foo' in attributes, attributes

    def test_list_dimensions(self):
        dimensions = list(self.state.dimensions)
        assert len(dimensions) == 4, dimensions
        assert 'amount' not in dimensions, dimensions
        assert 'function' in dimensions, dimensions
        assert not 'foo' in dimensions, dimensions


