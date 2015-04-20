from openspending.lib.helpers import url_for


def dataset_apply_links(dataset):
    dataset['html_url'] = url_for('dataset.view', dataset=dataset['name'])
    return dataset


def entry_apply_links(dataset_name, entry):
    if isinstance(entry, dict) and 'id' in entry:
        entry['html_url'] = url_for('entry.view', dataset=dataset_name,
                                    id=entry['id'])
        for k, v in entry.items():
            entry[k] = member_apply_links(dataset_name, k, v)
    return entry


def dimension_apply_links(dataset_name, dimension):
    name = dimension.get('name')
    dimension['html_url'] = url_for('dimension.view', dataset=dataset_name,
                                    dimension=name)
    return dimension


def member_apply_links(dataset_name, dimension, data):
    if isinstance(data, dict) and 'name' in data:
        name = unicode(data['name'])
        data['html_url'] = url_for('dimension.member', dataset=dataset_name,
                                   dimension=dimension, name=name)
    return data


def drilldowns_apply_links(dataset_name, drilldowns):
    linked_data = []
    for drilldown in drilldowns:
        for k, v in drilldown.items():
            drilldown[k] = member_apply_links(dataset_name, k, v)
        linked_data.append(drilldown)
    return linked_data
