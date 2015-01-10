import logging

from openspending.model.dimension import (CompoundDimension, DateDimension,
                                          AttributeDimension, Measure)

log = logging.getLogger(__name__)


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
        self.dimensions = []
        self.measures = []
        for dim, data in self.dataset.mapping.items():
            if data.get('type') == 'measure' or dim == 'amount':
                self.measures.append(Measure(self, dim, data))
                continue
            elif data.get('type') == 'date' or \
                    (dim == 'time' and data.get('datatype') == 'date'):
                dimension = DateDimension(self, dim, data)
            elif data.get('type') in ['value', 'attribute']:
                dimension = AttributeDimension(self, dim, data)
            else:
                dimension = CompoundDimension(self, dim, data)
            self.dimensions.append(dimension)

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
        return self.dimensions + self.measures

    @property
    def compounds(self):
        """ Return only compound dimensions. """
        return filter(lambda d: isinstance(d, CompoundDimension),
                      self.dimensions)

    @property
    def facet_dimensions(self):
        return [d for d in self.dimensions if d.facet]

    def __repr__(self):
        return "<Model(%r)>" % (self.dataset)
