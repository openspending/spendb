
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

    def __repr__(self):
        return "<Attribute(%s)>" % self.name

    def as_dict(self):
        return self._data
