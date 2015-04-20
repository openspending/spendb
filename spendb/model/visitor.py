from openspending.model.dimension import CompoundDimension, AttributeDimension
from openspending.model.dimension import DateDimension


class ModelVisitor(object):
    """ Traverse a ``Model``, potentially generating some other
    representation on the way. """

    def visit(self, model):
        self.model = model
        for measure in model.measures:
            self.visit_measure(measure)
        for dimension in model.dimensions:
            self.visit_dimension(dimension)

    def visit_attribute(self, attribute):
        pass

    def visit_measure(self, measure):
        self.visit_attribute(measure)

    def visit_attribute_dimension(self, dimension):
        self.visit_attribute(dimension)

    def visit_compound_dimension(self, dimension):
        for attribute in dimension.attributes:
            self.visit_attribute(attribute)

    def visit_date_dimension(self, dimension):
        self.visit_compound_dimension(dimension)

    def visit_dimension(self, dimension):
        if isinstance(dimension, AttributeDimension):
            self.visit_attribute_dimension(dimension)
        elif isinstance(dimension, DateDimension):
            self.visit_date_dimension(dimension)
        elif isinstance(dimension, CompoundDimension):
            self.visit_compound_dimension(dimension)
        
