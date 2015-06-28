import json
from itertools import count

from sqlalchemy import MetaData
from sqlalchemy.schema import Table, Column
from sqlalchemy.types import Unicode
from sqlalchemy.sql.expression import select

from spendb.core import db
from spendb.model.common import json_default
from spendb.validation.model import TYPES


class FactTable(object):
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
            self._table.append_column(id_col)
            json_col = Column('_json', Unicode())
            self._table.append_column(json_col)
            self._fields_columns(self._table)
        return self._table

    @property
    def alias(self):
        """ An alias used for queries. """
        if not hasattr(self, '_alias'):
            self._alias = self.table.alias('entry')
        return self._alias

    @property
    def mapping(self):
        if not hasattr(self, '_mapping'):
            self._mapping = {}
            for attribute in self.dataset.model.attributes:
                if attribute.column in self.alias.columns:
                    col = self.alias.c[attribute.column]
                    self._mapping[attribute.path] = col
        return self._mapping

    @property
    def exists(self):
        return db.engine.has_table(self.table.name)

    def _fields_columns(self, table):
        """ Transform the (auto-detected) fields into a set of column
        specifications. """
        for field in self.dataset.fields:
            data_type = TYPES.get(field.get('type'), Unicode)
            col = Column(field.get('name'), data_type, nullable=True)
            table.append_column(col)

    def load_iter(self, iterable, chunk_size=1000):
        """ Bulk load all the data in an artifact to a matching database
        table. """
        chunk = []

        conn = self.bind.connect()
        tx = conn.begin()
        try:
            for i, record in enumerate(iterable):
                chunk.append(self._expand_record(i, record))
                if len(chunk) >= chunk_size:
                    stmt = self.table.insert()
                    conn.execute(stmt, chunk)
                    chunk = []

            if len(chunk):
                stmt = self.table.insert()
                conn.execute(stmt, chunk)
            tx.commit()
        except:
            tx.rollback()
            raise

    def _expand_record(self, i, record):
        """ Transform an incoming record into a form that matches the
        fields schema. """
        record['_id'] = i
        record['_json'] = json.dumps(record, default=json_default)
        return record

    def unpack_entry(self, row):
        """ Convert a database-returned row into a nested and mapped
        fact representation. """
        row = dict(row.items())
        result = {'id': row.get('_id')}
        for dimension in self.dataset.model.dimensions:
            value = {}
            for attr in dimension.attributes:
                value[attr.name] = row.get(attr.column)
            result[dimension.name] = value
        for measure in self.dataset.model.measures:
            result[measure.name] = row.get(measure.column)
        return result

    def create(self):
        """ Create the fact table if it does not exist. """
        if not self.exists:
            self.table.create(self.bind)

    def drop(self):
        """ Drop the fact table if it does exist. """
        if self.exists:
            self.table.drop()
        self._table = None

    def num_entries(self):
        """ Get the number of facts that are currently loaded. """
        if not self.exists:
            return 0
        rp = self.bind.execute(self.table.count())
        return rp.fetchone()[0]

    def _dimension_columns(self, dimension):
        """ Filter the generated columns for those related to a
        particular dimension. """
        prefix = dimension.name + '.'
        columns = []
        for path, col in self.mapping.items():
            if path.startswith(prefix):
                columns.append(col)
        return columns

    def num_members(self, dimension):
        """ Get the number of members for the given dimension. """
        if not self.exists:
            return 0
        q = select(self._dimension_columns(dimension), distinct=True)
        rp = self.bind.execute(q.alias('counted').count())
        return rp.fetchone()[0]

    def dimension_members(self, dimension, conditions="1=1", offset=0,
                          limit=None):
        selects = self._dimension_columns(dimension)
        order_by = [s.asc() for s in selects]
        for entry in self.entries(conditions=conditions, order_by=order_by,
                                  selects=selects, distinct=True,
                                  offset=offset, limit=limit):
            yield entry.get(dimension.name)

    def entries(self, conditions="1=1", order_by=None, limit=None,
                selects=[], distinct=False, offset=0, step=10000):
        """ Generate a fully denormalized view of the entries on this
        table. This view is nested so that each dimension will be a hash
        of its attributes. """
        if not self.exists:
            return

        if not selects:
            selects = [self.alias.c._id] + self.mapping.values()

            # enforce stable sorting:
            if order_by is None:
                order_by = [self.alias.c._id.asc()]

        assert order_by is not None

        for i in count():
            qoffset = offset + (step * i)
            qlimit = step
            if limit is not None:
                qlimit = min(limit - (step * i), step)
            if qlimit <= 0:
                break

            query = select(selects, conditions, [], order_by=order_by,
                           distinct=distinct, limit=qlimit, offset=qoffset)
            rp = self.bind.execute(query)
            first_row = True
            while True:
                row = rp.fetchone()
                if row is None:
                    if first_row:
                        return
                    break
                first_row = False
                yield self.unpack_entry(row)

    def __repr__(self):
        return "<FactTable(%r)>" % (self.dataset)
