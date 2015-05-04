

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

    def visit_dimension(self, dimension):
        for attribute in dimension.attributes:
            self.visit_attribute(attribute)
