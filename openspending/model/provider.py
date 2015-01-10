from cubes.providers import ModelProvider
from cubes.model import Cube, Measure, MeasureAggregate, create_dimension
from cubes.backends.sql.store import SQLStore, OPTION_TYPES
from cubes.errors import NoSuchCubeError, NoSuchDimensionError
from cubes.common import coalesce_options
from cubes.logging import get_logger

from openspending.core import db
from openspending.model import Dataset
from openspending.model.visitor import ModelVisitor
from openspending.model.constants import FULL_DATE_CUBES_TEMPLATE, NUM_DATE_CUBES_TEMPLATE


class CubesModelVisitor(ModelVisitor):

    def __init__(self, dataset):
        self.mappings = {}
        self.dataset = dataset
        self.dimensions = []
        self.measures = []
        self.aggregates = [MeasureAggregate('num_entries',
                                            label='Numer of entries',
                                            function='count')]

    def visit_measure(self, measure):
        cubes_measure = Measure(measure.name, label=measure.label)
        self.measures.append(cubes_measure)
        aggregate = MeasureAggregate(measure.name,
                                     label=measure.label,
                                     measure=measure.name,
                                     function='sum')
        self.aggregates.append(aggregate)
        self.mappings[measure.name] = measure.column

    def add_dimension(self, dimension, meta):
        meta.update({'name': dimension.name, 'label': dimension.label})
        self.dimensions.append(create_dimension(meta))

    def visit_attribute_dimension(self, dimension):
        if dimension.column is None:
            return
        name = '%s.%s' % (dimension.name, dimension.name)
        self.mappings[name] = dimension.column
        self.add_dimension(dimension, {
            'levels': [{
                'name': dimension.name,
                'label': dimension.label,
                'key': dimension.name,
                'attributes': [dimension.name]
            }]
        })

    def visit_compound_dimension(self, dimension):
        attributes = []
        for attr in dimension.attributes:
            if attr.column is None:
                continue
            attributes.append(attr.name)
            name = '%s.%s' % (dimension.name, attr.name)
            self.mappings[name] = attr.column

        self.add_dimension(dimension, {
            'levels': [{
                'name': dimension.name,
                'label': dimension.label,
                'key': 'name',
                'attributes': attributes
            }]
        })

    def visit_date_dimension(self, dimension):
        if dimension.column is None:
            return
        field = self.dataset.fields.get(dimension.column, {})
        field_type = field.get('type')
        self.mappings['%s.name' % dimension.name] = dimension.column
        if field_type == 'date':
            for a in ['year', 'quarter', 'month', 'week', 'day']:
                name = '%s.%s' % (dimension.name, a)
                self.mappings[name] = {
                    'column': dimension.column,
                    'extract': a
                }
            self.add_dimension(dimension, FULL_DATE_CUBES_TEMPLATE)
        elif field_type == 'integer':
            self.mappings['%s.year' % dimension.name] = dimension.column
            self.add_dimension(dimension, NUM_DATE_CUBES_TEMPLATE)

    @property
    def table(self):
        return self.dataset.fact_table.table.name

    def generate_cube(self, store):
        self.visit(self.dataset.model)
        return Cube(name=self.dataset.name,
                    fact=self.table,
                    aggregates=self.aggregates,
                    measures=self.measures,
                    label=self.dataset.label,
                    description=self.dataset.description,
                    dimensions=self.dimensions,
                    store=store,
                    mappings=self.mappings)


class OpenSpendingModelProvider(ModelProvider):
    __extension_name__ = 'openspending'

    def __init__(self, *args, **kwargs):
        super(OpenSpendingModelProvider, self).__init__(*args, **kwargs)

    def requires_store(self):
        return True

    def cube(self, name, locale=None):
        dataset = Dataset.by_name(name)
        if name is None:
            raise NoSuchCubeError("Unknown dataset %s" % name, name)
        visitor = CubesModelVisitor(dataset)
        return visitor.generate_cube(self.store)

    def dimension(self, name, locale=None, templates=[]):
        raise NoSuchDimensionError('No global dimensions in OS', name)

    def list_cubes(self):
        cubes = []
        for dataset in Dataset.all_by_account(None):
            if not len(dataset.mapping):
                continue
            cubes.append({
                'name': dataset.name,
                'label': dataset.label
            })
        return cubes


class OpenSpendingStore(SQLStore):
    related_model_provider = "openspending"

    def model_provider_name(self):
        return self.related_model_provider

    def __init__(self, **options):
        super(SQLStore, self).__init__(**options)
        options = dict(options)
        self.options = coalesce_options(options, OPTION_TYPES)
        self.logger = get_logger()
        self.schema = None
        self._metadata = None

    @property
    def connectable(self):
        return db.engine
        
    @property
    def metadata(self):
        if self._metadata is None:
            self._metadata = db.MetaData(bind=self.connectable)
        return self._metadata
