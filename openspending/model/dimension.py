
from openspending.model.attribute import Attribute
from openspending.model.constants import DATE_CUBES_TEMPLATE
from openspending.model.common import df_column


class Dimension(object):
    """ A base class for dimensions. A dimension is any property of an entry
    that can serve to describe it beyond its purely numeric ``Measures``.  """

    def __init__(self, model, name, data):
        self._data = data
        self.model = model
        self.name = name
        self.label = data.get('label', name)
        self.type = data.get('type', name)
        self.description = data.get('description', name)
        self.facet = data.get('facet')

    def __getitem__(self, name):
        raise KeyError()

    def __repr__(self):
        return "<Dimension(%s)>" % self.name

    def as_dict(self):
        # FIXME: legacy support
        d = self._data.copy()
        d['key'] = self.name
        d['name'] = self.name
        return d


class AttributeDimension(Dimension, Attribute):
    """ A simple dimension that does not create its own values table
    but keeps its values directly as columns on the facts table. This is
    somewhat unusual for a star schema but appropriate for properties such as
    transaction identifiers whose cardinality roughly equals that of the facts
    table.
    """

    def __init__(self, model, name, data):
        Attribute.__init__(self, model, name, data)
        Dimension.__init__(self, model, name, data)

    def __repr__(self):
        return "<AttributeDimension(%s)>" % self.name

    def to_cubes(self, mappings, joins):
        """ Convert this dimension to a ``cubes`` dimension. """
        mappings['%s.%s' % (self.name, self.name)] = unicode(self.column)
        return {
            'levels': [{
                'name': self.name,
                'label': self.label,
                'key': self.name,
                'attributes': [self.name]
            }]
        }


class Measure(Attribute):
    """ A value on the facts table that can be subject to aggregation,
    and is specific to this one fact. This would typically be some
    financial unit, i.e. the amount associated with the transaction or
    a specific portion thereof (i.e. co-financed amounts). """

    def __init__(self, model, name, data):
        Attribute.__init__(self, model, name, data)
        self.label = data.get('label', name)

    def __getitem__(self, name):
        raise KeyError()

    def __repr__(self):
        return "<Measure(%s)>" % self.name


class CompoundDimension(Dimension):
    """ A compound dimension is an outer table on the star schema, i.e. an
    associated table that is referenced from the fact table. It can have
    any number of attributes but in the case of OpenSpending it will not
    have sub-dimensions (i.e. snowflake schema).
    """

    def __init__(self, model, name, data):
        Dimension.__init__(self, model, name, data)
        # self.taxonomy = data.get('taxonomy', name)

        self.attributes = []
        for name, attr in data.get('attributes', {}).items():
            self.attributes.append(Attribute(self, name, attr))

    @property
    def columns(self):
        return [a.column for a in self.attributes]

    def __getitem__(self, name):
        for attr in self.attributes:
            if attr.name == name:
                return attr
        raise KeyError()

    def to_cubes(self, mappings, joins):
        """ Convert this dimension to a ``cubes`` dimension. """
        attributes = ['id'] + [a.name for a in self.attributes]
        fact_table = self.model.dataset.name + '__entry'
        joins.append({
            'master': '%s.%s' % (fact_table, self.name + '_id'),
            'detail': '%s.id' % self.table.name
        })
        for a in attributes:
            mappings['%s.%s' % (self.name, a)] = '%s.%s' % (self.table.name, a)

        return {
            'levels': [{
                'name': self.name,
                'label': self.label,
                'key': 'name',
                'attributes': attributes
            }]
        }

    def __repr__(self):
        return "<CompoundDimension(%s:%s)>" % (self.name, self.attributes)


class DateDimension(CompoundDimension):

    """ DateDimensions are closely related to :py:class:`CompoundDimensions`
    but the value is set up from a Python date object to automatically contain
    several properties of the date in their own attributes (e.g. year, month,
    quarter, day). """

    DATE_ATTRIBUTES = {
        'name': {'datatype': 'string'},
        'label': {'datatype': 'string'},
        'year': {'datatype': 'string'},
        'quarter': {'datatype': 'string'},
        'month': {'datatype': 'string'},
        'week': {'datatype': 'string'},
        'day': {'datatype': 'string'}
    }

    def __init__(self, model, name, data):
        Dimension.__init__(self, model, name, data)
        self.column = data.get('column')

        self.attributes = []
        for attr_name, attr in self.DATE_ATTRIBUTES.items():
            attr = Attribute(self, attr_name, attr)
            attr.column = df_column(name, attr_name)
            self.attributes.append(attr)

    @property
    def columns(self):
        return [self.column]

    def to_cubes(self, mappings, joins):
        """ Convert this dimension to a ``cubes`` dimension. """
        fact_table = self.model.dataset.name + '__entry'
        joins.append({
            'master': '%s.%s' % (fact_table, self.name + '_id'),
            'detail': '%s.id' % self.table.name
        })
        for a in ['name', 'year', 'quarter', 'month', 'week', 'day']:
            mappings['%s.%s' % (self.name, a)] = '%s.%s' % (self.table.name, a)
        return DATE_CUBES_TEMPLATE.copy()

    def __repr__(self):
        return "<DateDimension(%s)>" % self.name
