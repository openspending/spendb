import logging
import random
from decimal import Decimal
from datetime import datetime, date

from loadkit.operators.table import resource_row_set
from loadkit.operators.table import generate_field_spec

log = logging.getLogger(__name__)


def date_field(name, section):
    return '%s__%s' % (name, section)


def field_transform(fields):
    spec = {}
    for field in fields:
        # have mercy:
        if field['type'] == 'decimal':
            field['type'] = 'float'

        if field['type'] == 'date':
            for section in ['year', 'month', 'day']:
                name = date_field(field['name'], section)
                spec[name] = {
                    'name': name,
                    'type': 'integer',
                    'title': '%s (%s)' % (field['title'], section)
                }
            name = date_field(field['name'], 'label')
            spec[name] = {
                'name': name,
                'type': 'string',
                'title': field['title']
            }
        else:
            spec[field['name']] = field
    return spec


def random_sample(data, samples, row, num=10):
    """ Collect a random sample of the rows based on reservoir sampling. """
    if len(samples) < num:
        samples.append(data)
    else:
        j = random.randint(0, row)
        if j < (num - 1):
            samples[j] = data


def parse_table(row_set):
    fields, fields_dict, samples = {}, {}, []

    for i, row in enumerate(row_set):
        if not len(fields):
            fields = generate_field_spec(row)
            fields_dict = field_transform(fields)

        data = {}
        for cell, field in zip(row, fields):
            value = cell.value
            if field['type'] == 'date':
                values = None, None, None, None
                if isinstance(value, datetime):
                    value = value.date()
                if isinstance(value, date):
                    values = value.year, value.month, value.day, \
                        value.isoformat()
                data[date_field(field['name'], 'year')] = values[0]
                data[date_field(field['name'], 'month')] = values[1]
                data[date_field(field['name'], 'day')] = values[2]
                data[date_field(field['name'], 'label')] = values[3]
            else:
                if isinstance(value, Decimal):
                    # Baby jesus forgive me.
                    value = float(value)
                if isinstance(value, basestring) and not len(value.strip()):
                    value = None
                data[field['name']] = value

        check_empty = set(data.values())
        if None in check_empty and len(check_empty) == 1:
            continue

        random_sample(data, samples, i)
        yield fields_dict, data, samples


def extract_table(source, table):
    row_set = resource_row_set(source.package, source)
    if row_set is None:
        return table

    with table.store() as save_func:
        for i, (fields, row, samples) in enumerate(parse_table(row_set)):
            save_func(row)

    log.info("Converted %s rows with %s columns.", i, len(fields))
    table.meta['fields'] = fields
    table.meta['samples'] = samples
    table.meta['num_records'] = i
    table.meta.save()
    return table
