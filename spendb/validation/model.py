from spendb.validation.common import mapping as mapping_node, \
    ValidationState
from spendb.validation.dataset import dataset_schema
from spendb.validation.mapping import mapping_schema


def model_schema(state):
    schema = mapping_node('model')
    schema.add(dataset_schema(state))
    schema.add(mapping_schema(state))
    return schema


def validate_model(model):
    """ Apply model validation. """
    state = ValidationState(model)
    schema = model_schema(state)
    return schema.deserialize(model)
