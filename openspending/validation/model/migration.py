
SCHEMA_FIELD = 'schema_version'


def migrate_model(model):
    model['dataset'] = model.get('dataset', {})
    version = model['dataset'].get(SCHEMA_FIELD, '1970-01-01')
    for k, func in sorted(MIGRATIONS.items()):
        if k > version:
            model = func(model)
    model['dataset'][SCHEMA_FIELD] = max(MIGRATIONS.keys())
    return model


def m2011_11_20_require_name_attribute(model):
    # https://github.com/okfn/openspending/issues/209
    for name, meta in model.get('mapping', {}).items():
        label_column = None
        label_default = None
        has_name = False
        if not 'fields' in meta:
            continue
        for field in meta['fields']:
            if field['name'] == 'name':
                has_name = True
            elif field['name'] == 'label':
                label_column = field.get('column')
                label_default = field.get('default_value')
        if (not has_name) and label_column:
            field = {
                'name': 'name',
                'datatype': 'id',
                'column': label_column,
                }
            if label_default:
                field['default_value'] = label_default
            meta['fields'].append(field)
        model['mapping'][name] = meta
    return model


def m2011_11_21_normalize_types(model):
    def _tf(name, meta, type_):
        if type_ in ['measure', 'date']:
            return meta
        if type_ in ['value']:
            if name == 'amount':
                meta['type'] = 'measure'
            elif name == 'time':
                meta['type'] = 'date'
            else:
                meta['type'] = 'attribute'
            return meta
        if 'attributes' in meta or 'fields' in meta:
            meta['type'] = 'compound'
        else:
            meta['type'] = 'attribute'
        return meta

    for name, meta in model.get('mapping', {}).items():
        type_ = meta.get('type', '').lower().strip()
        meta['type'] = type_
        model['mapping'][name] = _tf(name, meta, type_)
    return model


def m2011_11_22_unique_keys(model):
    if 'unique_keys' in model.get('dataset', {}):
        for key in model['dataset']['unique_keys']:
            key = key.split('.')[0]
            if key in model['mapping']:
                model['mapping'][key]['key'] = True
        del model['dataset']['unique_keys']
    return model


def m2011_12_07_attributes_dictionary(model):
    for name, meta in model.get('mapping', {}).items():
        if ('attributes' not in meta) and ('fields' in meta):
            meta['attributes'] = {}
            for field in meta.get('fields', []):
                if 'name' not in field:
                    continue
                name_ = field['name']
                del field['name']
                meta['attributes'][name_] = field
            del meta['fields']
        model['mapping'][name] = meta
    return model


def m2012_05_29_add_category(model):
    if not model['dataset'].get('category'):
        model['dataset']['category'] = 'other'
    return model


MIGRATIONS = {
    '2011-11-20': m2011_11_20_require_name_attribute,
    '2011-11-21': m2011_11_21_normalize_types,
    '2011-11-22': m2011_11_22_unique_keys,
    '2011-12-07': m2011_12_07_attributes_dictionary,
    '2012-05-29': m2012_05_29_add_category,
    }
