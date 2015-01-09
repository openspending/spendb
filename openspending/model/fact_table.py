"""
The ``FactTable`` serves as a controller object for a given ``Model``,
handling the creation, filling and migration of the table schema
associated with the dataset.
"""
import logging
from datetime import datetime
from itertools import count
from sqlalchemy import ForeignKeyConstraint, MetaData
from sqlalchemy.types import Unicode
from sqlalchemy.sql.expression import select, func

from openspending.core import db
from openspending.lib.util import hash_values

from openspending.model.common import decode_row, TableHandler
from openspending.model.dimension import CompoundDimension

log = logging.getLogger(__name__)


class FactTable(TableHandler):

    def __init__(self, dataset, model):
        self.dataset = dataset
        self.model = model
        self.init()

    def init(self):
        """ Create a SQLAlchemy model for the current dataset model,
        without creating the tables and columns. This needs to be
        called both for access to the data and in order to generate
        the model physically. """
        self.bind = db.engine
        # HACK HACK LOOSE WHEN THERE'S ONLY ONE FACT TABLE:
        self.model.bind = self.bind
        self.meta = MetaData()
        self.meta.bind = self.bind
        
        self._init_table(self.meta, self.dataset.name, 'entry',
                         id_type=Unicode(42))
        for field in self.model.fields:
            field.column = field.init(self.meta, self.table)
        self.alias = self.table.alias('entry')
        # HACK HACK LOOSE WHEN THERE'S ONLY ONE FACT TABLE:
        self.model.alias = self.alias
        self._is_generated = None

    def generate(self):
        """ Create the tables and columns necessary for this dataset
        to keep data.
        """
        for field in self.model.fields:
            field.generate(self.meta, self.table)
        for dim in self.model.dimensions:
            if isinstance(dim, CompoundDimension):
                self.table.append_constraint(ForeignKeyConstraint(
                    [dim.name + '_id'], [dim.table.name + '.id'],
                    # use_alter=True,
                    name='fk_' + self.dataset.name + '_' + dim.name
                ))
        self._generate_table()
        self._is_generated = None

    @property
    def is_generated(self):
        if self._is_generated is None:
            self._is_generated = self.table.exists()
        return self._is_generated

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

    def load(self, data):
        """ Handle a single entry of data in the mapping source format,
        i.e. with all needed columns. This will propagate to all dimensions
        and set values as appropriate. """
        entry = dict()
        for field in self.model.fields:
            field_data = data[field.name]
            entry.update(field.load(self.bind, field_data))
        entry['id'] = self.model._make_key(data)
        self._upsert(self.bind, entry, ['id'])

    def drop(self):
        """ Drop all tables created as part of this dataset, i.e. by calling
        ``generate()``. This will of course also delete the data itself.
        """
        self._drop(self.bind)
        for dimension in self.model.dimensions:
            dimension.drop(self.bind)
        self._is_generated = False

    def key(self, key):
        """ For a given ``key``, find a column to indentify it in a query.
        A ``key`` is either the name of a simple attribute (e.g. ``time``)
        or of an attribute of a complex dimension (e.g. ``to.label``). The
        returned key is using an alias, so it can be used in a query
        directly. """
        attr = None
        if '.' in key:
            key, attr = key.split('.', 1)
        dimension = self.model[key]
        if hasattr(dimension, 'alias'):
            attr_name = dimension[attr].column.name if attr else 'name'
            return dimension.alias.c[attr_name]
        return self.alias.c[dimension.column.name]

    def entries(self, conditions="1=1", order_by=None, limit=None,
                offset=0, step=10000, fields=None):
        """ Generate a fully denormalized view of the entries on this
        table. This view is nested so that each dimension will be a hash
        of its attributes.

        This is somewhat similar to the entries collection in the fully
        denormalized schema before OpenSpending 0.11 (MongoDB).
        """
        if not self.is_generated:
            return

        if fields is None:
            fields = self.model.fields

        joins = self.alias
        for d in self.model.dimensions:
            if d in fields:
                joins = d.join(joins)
        selects = [f.selectable for f in fields] + [self.alias.c.id]

        # enforce stable sorting:
        if order_by is None:
            order_by = [self.alias.c.id.asc()]

        for i in count():
            qoffset = offset + (step * i)
            qlimit = step
            if limit is not None:
                qlimit = min(limit - (step * i), step)
            if qlimit <= 0:
                break

            query = select(selects, conditions, joins, order_by=order_by,
                           use_labels=True, limit=qlimit, offset=qoffset)
            rp = self.bind.execute(query)

            first_row = True
            while True:
                row = rp.fetchone()
                if row is None:
                    if first_row:
                        return
                    break
                first_row = False
                yield decode_row(row, self)

    def timerange(self):
        """
        Get the timerange of the dataset (based on the time attribute).
        Returns a tuple of (first timestamp, last timestamp) where timestamp
        is a datetime object
        """
        try:
            # Get the time column
            time = self.key('time')
            # We use SQL's min and max functions to get the timestamps
            query = db.session.query(func.min(time), func.max(time))
            # We just need one result to get min and max time
            return [datetime.strptime(date, '%Y-%m-%d') if date else None
                    for date in query.one()]
        except:
            return (None, None)

    def num_entries(self):
        if not self.is_generated:
            return 0
        rp = self.bind.execute(self.alias.count())
        return rp.fetchone()[0]

    def __repr__(self):
        return "<FactTable(%r)>" % (self.dataset)
