from sqlalchemy import MetaData
from sqlalchemy.schema import Table, Column
from sqlalchemy.types import Unicode

from openspending.core import db


class DenormFactTable(object):
    """ The ``FactTable`` serves as a controller object for
    a given ``Model``, handling the creation, filling and migration
    of the table schema associated with the dataset. """
    
    def __init__(self, dataset):
        self.dataset = dataset
        
        self.bind = db.engine
        self.meta = MetaData()
        self.meta.bind = self.bind
        self._table = None
        
    @property
    def table(self):
        """ Generate an appropriate table representation to mirror the
        fields known for this table. """
        if self._table is None:
            name = '%s__facts' % self.dataset.name
            self._table = Table(name, self.meta)
            id_col = Column('_id', Unicode(42), primary_key=True)
            self.table.append_column(id_col)

        return self._table

    def create(self):
        """ Create the fact table if it does not exist. """
        if not db.engine.has_table(self.table.name):
            self.table.create(db.engine)

    def drop(self):
        """ Drop the fact table if it does exist. """
        if db.engine.has_table(self.table.name):
            self.table.drop()
        self._table = None

