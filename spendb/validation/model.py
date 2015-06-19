from colander import All, MappingSchema, Schema, String, SchemaNode
from colander import Boolean, drop, Length, OneOf, Function

from spendb.core import db
from spendb.validation.common import field_name, require_one_child


TYPES = {
    'string': db.Unicode,
    'integer': db.BigInteger,
    'float': db.Float
}

CARDINALITIES = ['tiny', 'low', 'medium', 'high']


def create_named_node(stub, name):
    """ Create an ad-hoc node to represent a mapping item with
    the given name. """
    clone = stub.clone()
    clone.name = name
    valid = lambda n, v: field_name(n, name)
    if clone.validator is not None:
        valid = All(clone.validator, valid)
    clone.validator = valid
    return clone


def generate_mappings(node, kw):
    """ Hack colander to generate schema on the fly, based on the model
    that has been submitted. """
    if not hasattr(node, 'bound_data'):
        node.bound_data = kw.get('data')

    if not hasattr(node.bound_data, 'items'):
        return

    children = []
    for child in node.children:
        if child.name == '_named':
            for key, value in node.bound_data.items():
                children.append(create_named_node(child, key))
        else:
            children.append(child)
    node.children = children

    for child in node.children:
        child.bound_data = node.bound_data.get(child.name)
        generate_mappings(child, kw)


class Attribute(MappingSchema):
    label = SchemaNode(String(), missing=drop)
    description = SchemaNode(String(), missing='')
    column = SchemaNode(String(), validator=Length(min=1))
    type = SchemaNode(String(), missing='string',
                      validator=OneOf(TYPES.keys()))


class Attributes(MappingSchema):
    _named = Attribute()


class Dimension(MappingSchema):
    label = SchemaNode(String(), missing=drop)
    description = SchemaNode(String(), missing='')
    facet = SchemaNode(Boolean(), missing=False)
    cardinality = SchemaNode(String(), missing='high',
                             validator=OneOf(CARDINALITIES))
    attributes = Attributes(validator=Function(require_one_child))


class Dimensions(MappingSchema):
    _named = Dimension()


class Measure(Attribute):
    type = SchemaNode(String(), missing='integer',
                      validator=OneOf(['integer', 'float']))


class Measures(MappingSchema):
    _named = Measure()


class Model(Schema):
    dimensions = Dimensions(validator=Function(require_one_child))
    measures = Measures(validator=Function(require_one_child))


def validate_model(model):
    """ Apply model validation. """
    schema = Model(after_bind=generate_mappings)
    schema = schema.bind(data=model)
    return schema.deserialize(model)
