import os
import json
from normality import slugify

DIR = 'exports'


def slug(name):
    return slugify(name, sep='_')


def list_datasets():
    for name in os.listdir(DIR):
        ds_dir = os.path.join(DIR, name)
        with open(os.path.join(ds_dir, 'dataset.json'), 'rb') as fh:
            meta = json.load(fh)
            yield ds_dir, meta


def transform_dataset(source):
    mapping = source['data']['mapping']
    model = {'measures': {}, 'dimensions': {}}
    types = set()
    for name, src in mapping.items():
        norm_name = slug(name)
        if src.get('type') == 'measure':
            model['measures'][norm_name] = {
                'label': src['label'],
                'description': src['description'] or '',
                'column': norm_name
            }
            continue

        dim = {
            'label': src['label'],
            'description': src['description'] or '',
            'label_attribute': 'label',
            'key_attribute': 'label',
            'attributes': {}
        }
        if src.get('type') == 'date':
            dim['attributes'] = {
                'label': {
                    'label': 'Label',
                    'column': norm_name + '_name'
                },
                'year': {
                    'label': 'Year',
                    'column': norm_name + '_year'
                },
                'month': {
                    'label': 'Month',
                    'column': norm_name + '_month'
                },
                'day': {
                    'label': 'Day',
                    'column': norm_name + '_day'
                },
                'yearmonth': {
                    'label': 'Year/Month',
                    'column': norm_name + '_yearmonth'
                }
            }
        if src.get('type') == 'attribute':
            dim['attributes'] = {
                'label': {
                    'label': 'Label',
                    'column': norm_name
                }
            }
        if src.get('type') == 'compound':
            for name, spec in src['attributes'].items():
                attr = slug(name)
                dim['attributes'][attr] = {
                    'label': spec['column'],
                    'column': norm_name + '_' + attr
                }
            if 'name' in dim['attributes']:
                dim['key_attribute'] = 'name'
        model['dimensions'][norm_name] = dim
    return model


if __name__ == '__main__':
    for dir, ds in list_datasets():
        data = transform_dataset(ds)
        with open(os.path.join(dir, 'model.json'), 'wb') as fh:
            json.dump(data, fh, indent=2)
