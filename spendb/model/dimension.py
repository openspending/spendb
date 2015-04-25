
class Attribute(object):
    """ An attribute describes some concrete value stored in the data model.
    This value can either be stored directly on the facts table or on a
    separate dimension table, which is associated to the facts table through
    a reference. """

    def __init__(self, parent, name, data):
        self._data = data
        self.parent = parent
        self.name = name
        self.column = data.get('column')
        self.description = data.get('description')

    @property
    def path(self):
        if isinstance(self.parent, Dimension):
            return '%s.%s' % (self.parent.name, self.name)
        return self.name

    def __repr__(self):
        return "<Attribute(%s)>" % self.name

    def as_dict(self):
        return self._data


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
    any number of attributes but will not have sub-dimensions (i.e. snowflake
    schema). """

    def __init__(self, model, name, data):
        Dimension.__init__(self, model, name, data)
        # self.taxonomy = data.get('taxonomy', name)

        self.attributes = []
        for name, attr in data.get('attributes', {}).items():
            self.attributes.append(Attribute(self, name, attr))

    def __getitem__(self, name):
        for attr in self.attributes:
            if attr.name == name:
                return attr
        raise KeyError()

    def __repr__(self):
        return "<CompoundDimension(%s:%s)>" % (self.name, self.attributes)


class DateDimension(CompoundDimension):
    """ DateDimensions are closely related to :py:class:`CompoundDimensions`
    but the value is set up from a Python date object to automatically contain
    several properties of the date in their own attributes (e.g. year, month,
    quarter, day). """

    DATE_ATTRIBUTES = ['name', 'label', 'year', 'quarter', 'month', 'week',
                       'day']

    def __init__(self, model, name, data):
        Dimension.__init__(self, model, name, data)
        self.column = data.get('column')

        self.attributes = []
        for attr_name in self.DATE_ATTRIBUTES:
            attr = Attribute(self, attr_name, {})
            attr.column = '_df_%s_%s' % (name, attr_name)
            self.attributes.append(attr)

    def __repr__(self):
        return "<DateDimension(%s)>" % self.name
