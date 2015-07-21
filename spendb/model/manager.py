from babbage.manager import CubeManager

from spendb.core import db
from spendb.model.dataset import Dataset


class SpendingCubeManager(CubeManager):
    """ This enables the babbage API to find and query SpenDB datasets """

    def __init__(self):
        pass

    def has_cube(self, name):
        dataset = Dataset.by_name(name)
        if dataset is None:
            return False
        return dataset.has_model

    def get_cube_model(self, name):
        dataset = Dataset.by_name(name)
        if dataset is None or not dataset.has_model:
            return None
        model_data = dataset.model_data
        model_data['fact_table'] = dataset.fact_table.table_name
        return model_data

    def get_engine(self):
        return db.engine

    def list_cubes(self):
        # TODO: authz, failing conservatively for now.
        for dataset in Dataset.all_by_account(None):
            if dataset.has_model:
                yield dataset.name
