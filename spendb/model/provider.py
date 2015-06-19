from cubes.providers import ModelProvider, link_cube
from cubes.model import Cube, Measure, MeasureAggregate, Dimension
from cubes.sql.store import SQLStore, OPTION_TYPES
from cubes.errors import NoSuchCubeError, NoSuchDimensionError
from cubes.common import coalesce_options
from cubes.logging import get_logger

from spendb.core import db
from spendb.model import Dataset


class SpendingModelProvider(ModelProvider):

    def __init__(self, *args, **kwargs):
        super(SpendingModelProvider, self).__init__(*args, **kwargs)

    def requires_store(self):
        return True

    def has_cube(self, name):
        dataset = Dataset.by_name(name)
        return dataset is not None

    def cube(self, name, locale=None, namespace=None):
        dataset = Dataset.by_name(name)
        if name is None:
            raise NoSuchCubeError("Unknown dataset %s" % name, name)

        measures, dimensions, mappings = [], [], {}
        aggregates = [MeasureAggregate('fact_count',
                                       label='Number of entries',
                                       function='count')]

        for measure in dataset.model.measures:
            cubes_measure = Measure(measure.name, label=measure.label)
            measures.append(cubes_measure)
            aggregate = MeasureAggregate(measure.name + '_sum',
                                         label=measure.label,
                                         measure=measure.name,
                                         function='sum')
            aggregates.append(aggregate)
            mappings[measure.name] = measure.column

        for dimension in dataset.model.dimensions:
            attributes, last_col = [], None
            for attr in dimension.attributes:
                attributes.append({
                    'name': attr.name,
                    'label': attr.label
                })
                mappings[attr.path] = last_col = attr.column

            # Workaround because the cubes mapper shortens references
            # for single-attribute dimensions to just the dimension name.
            if len(attributes) == 1:
                mappings[dimension.name] = last_col

            # Translate into cubes' categories
            cardinality = 'high'
            if dimension.cardinality:
                if dimension.cardinality < 6:
                    cardinality = 'tiny'
                elif dimension.cardinality < 51:
                    cardinality = 'low'
                elif dimension.cardinality < 1001:
                    cardinality = 'medium'

            meta = {
                'label': dimension.label,
                'name': dimension.name,
                'cardinality': cardinality,
                'levels': [{
                    'name': dimension.name,
                    'label': dimension.label,
                    'cardinality': cardinality,
                    # 'key': 'name',
                    'attributes': attributes
                }]
            }
            dimensions.append(Dimension.from_metadata(meta))

        cube = Cube(name=dataset.name,
                    fact=dataset.fact_table.table.name,
                    aggregates=aggregates,
                    measures=measures,
                    label=dataset.label,
                    description=dataset.description,
                    dimensions=dimensions,
                    store=self.store,
                    mappings=mappings)

        link_cube(cube, locale, provider=self, namespace=namespace)
        return cube

    def dimension(self, name, locale=None, templates=[]):
        raise NoSuchDimensionError('No global dimensions in OS', name)

    def list_cubes(self):
        cubes = []
        for dataset in Dataset.all_by_account(None):
            if not len(dataset.model.axes):
                continue
            cubes.append({
                'name': dataset.name,
                'label': dataset.label
            })
        return cubes


class SpendingStore(SQLStore):
    related_model_provider = "spending"

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
