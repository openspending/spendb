import logging

log = logging.getLogger(__name__)


class Attribute(object):
    """ An attribute describes some concrete value stored in the data model.
    This value will be stored directly on the facts table as a column. """

    def __init__(self, parent, name, data):
        self.parent = parent
        self.name = name
        self.data = data
        self.label = data.get('label', name)
        self.column = data.get('column')
        self.description = data.get('description')

    @property
    def path(self):
        return '%s.%s' % (self.parent.name, self.name)

    def __repr__(self):
        return "<Attribute(%s)>" % self.name

    def to_dict(self):
        return self.data


class Dimension(object):
    """ A dimension is any property of an entry that can serve to describe
    it beyond its purely numeric ``Measures``. It is defined by several
    attributes, which contain actual values. """

    def __init__(self, model, name, data):
        self.data = data
        self.model = model
        self.name = name
        self.label = data.get('label', name)
        self.description = data.get('description', name)
        self.cardinality = data.get('cardinality', 'high')

    @property
    def attributes(self):
        for name, attr in self.data.get('attributes', {}).items():
            yield Attribute(self, name, attr)

    def __repr__(self):
        return "<Dimension(%s)>" % self.name

    def to_dict(self):
        return self.data.copy()


class Measure(Attribute):
    """ A value on the facts table that can be subject to aggregation,
    and is specific to this one fact. This would typically be some
    financial unit, i.e. the amount associated with the transaction or
    a specific portion thereof (i.e. co-financed amounts). """

    def __init__(self, model, name, data):
        Attribute.__init__(self, model, name, data)

    @property
    def path(self):
        return self.name

    def __repr__(self):
        return "<Measure(%s)>" % self.name


class Model(object):
    """ The ``Model`` serves as an abstract representation of a dataset,
    representing its measures, dimensions and attributes. """

    def __init__(self, dataset):
        """ Construct the in-memory object representation of this
        dataset's dimension and measures model.

        This is called upon initialization and deserialization of
        the dataset from the SQLAlchemy store.
        """
        self.dataset = dataset

    @property
    def dimensions(self):
        for name, data in self.dataset.model_data.get('dimensions', {}).items():
            yield Dimension(self, name, data)

    @property
    def measures(self):
        for name, data in self.dataset.model_data.get('measures', {}).items():
            yield Measure(self, name, data)

    @property
    def attributes(self):
        for measure in self.measures:
            yield measure
        for dimension in self.dimensions:
            for attribute in dimension.attributes:
                yield attribute

    @property
    def exists(self):
        return len(self.axes) > 0

    def __getitem__(self, name):
        """ Access a axis (dimension or measure) by name. """
        for axis in self.axes:
            if axis.name == name:
                return axis
        raise KeyError()

    def __contains__(self, name):
        try:
            self[name]
            return True
        except KeyError:
            return False

    @property
    def axes(self):
        """ Both the dimensions and metrics in this dataset. """
        return list(self.dimensions) + list(self.measures)

    def __repr__(self):
        return "<Model(%r)>" % (self.dataset)
