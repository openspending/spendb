import os
import logging
import random
from decimal import Decimal
from datetime import datetime

from messytables import type_guess, types_processor, headers_guess
from messytables import headers_processor, offset_processor

from loadkit.operators.table import column_alias, resource_row_set

log = logging.getLogger(__name__)


def generate_field_spec(row):
    """ Generate a set of metadata for each field/column in
    the data. This is loosely based on jsontableschema. """
    names = set()
    fields = []
    for cell in row:
        name = column_alias(cell, names)
        field = {
            'name': name,
            'title': cell.column,
            'type': unicode(cell.type).lower()
        }
        if hasattr(cell.type, 'format'):
            field['type'] = 'date'
            field['format'] = cell.type.format
        fields.append(field)
    return fields


def random_sample(data, samples, row, num=10):
    """ Collect a random sample of the values in a particular
    field based on the reservoir sampling technique. """
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
            print 'ROW', row
            fields = generate_field_spec(row)
            fields_dict = {f.get('name'): f for f in fields}

        data = {}
        for cell, field in zip(row, fields):
            value = cell.value
            if isinstance(value, datetime):
                value = value.date()
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
