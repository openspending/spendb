
SCHEMA_FIELD = 'schema_version'


def migrate_model(model):
    model['dataset'] = model.get('dataset', {})
    version = model['dataset'].get(SCHEMA_FIELD, '1970-01-01')
    for k, func in sorted(MIGRATIONS.items()):
        if k > version:
            model = func(model)
    model['dataset'][SCHEMA_FIELD] = max(MIGRATIONS.keys() + [version])
    return model


MIGRATIONS = {}
