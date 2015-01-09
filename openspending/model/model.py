"""
The ``Model`` serves as an abstract representation of a dataset,
representing its measures, dimensions and attributes.
"""
import logging

from openspending.lib.util import hash_values
from openspending.model.dimension import (CompoundDimension, DateDimension,
                                          AttributeDimension, Measure)

log = logging.getLogger(__name__)


class Model(object):

    def __init__(self, dataset):
        self.dataset = dataset
        self.init()

    def init(self):
        """ Construct the in-memory object representation of this
        dataset's dimension and measures model.

        This is called upon initialization and deserialization of
        the dataset from the SQLAlchemy store.
        """
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

    def __getitem__(self, name):
        """ Access a field (dimension or measure) by name. """
        for field in self.fields:
            if field.name == name:
                return field
        raise KeyError()

    def __contains__(self, name):
        try:
            self[name]
            return True
        except KeyError:
            return False

    @property
    def fields(self):
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

    def _make_key(self, data):
        """ Generate a unique identifier for an entry. This is better
        than SQL auto-increment because it is stable across mutltiple
        loads and thus creates stable URIs for entries.
        """
        uniques = [self.dataset.name]
        for field in self.fields:
            if not field.key:
                continue
            obj = data.get(field.name)
            if isinstance(obj, dict):
                obj = obj.get('name', obj.get('id'))
            uniques.append(obj)
        return hash_values(uniques)

    def __repr__(self):
        return "<Model(%r)>" % (self.dataset)
