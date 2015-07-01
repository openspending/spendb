import logging
import random
from decimal import Decimal
from datetime import datetime

from normality import slugify
import messytables as mt
from messytables.jts import celltype_as_string

log = logging.getLogger(__name__)


def column_alias(cell, names):
    """ Generate a normalized version of the column name. """
    column = slugify(cell.column or '', sep='_')
    column = column.strip('_')
    column = 'column' if not len(column) else column
    name, i = column, 2
    # de-dupe: column, column_2, column_3, ...
    while name in names:
        name = '%s_%s' % (name, i)
        i += 1
    return name


def generate_field_spec(row):
    """ Generate a set of metadata for each field/column in
    the data. This is conformant to jsontableschema. """
    names = set()
    fields = []
    for cell in row:
        name = column_alias(cell, names)
        field = {
            'name': name,
            'title': cell.column,
            'type': celltype_as_string(cell.type),
            'has_empty': False,
            'samples': []
        }
        if hasattr(cell.type, 'format'):
            field['format'] = cell.type.format
        fields.append(field)
    return fields


def random_sample(value, field, row, num=10):
    """ Collect a random sample of the values in a particular
    field based on the reservoir sampling technique. """
    # TODO: Could become a more general DQ piece.
    if value in field['samples']:
        return
    if value is None:
        field['has_empty'] = True
        return
    if len(field['samples']) < num:
        field['samples'].append(value)
        return
    j = random.randint(0, row)
    if j < (num - 1):
        field['samples'][j] = value


def convert_row(row, fields, i):
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
        random_sample(value, field, i)
        data[field['name']] = value
    return data


def parse_table(source):
    # This is a work-around because messytables hangs on boto file
    # handles, so we're doing it via plain old HTTP.
    # We're also passing in an extended window size to give more
    # reliable type detection.
    # Because Python's CSV dialect sniffer isn't the best, this also
    # constrains the field quoting character to a double quote.
    table_set = mt.any_tableset(source.fh(),
                                extension=source.meta.get('extension'),
                                mimetype=source.meta.get('mime_type'),
                                quotechar='"', window=20000)
    tables = list(table_set.tables)
    if not len(tables):
        log.error("No tables were found in the source file.")
        return
    row_set = tables[0]
    headers = [c.value for c in next(row_set.sample)]
    row_set.register_processor(mt.headers_processor(headers))
    row_set.register_processor(mt.offset_processor(1))
    types = mt.type_guess(row_set.sample, strict=True)
    row_set.register_processor(mt.types_processor(types, strict=True))

    fields, i = {}, 0
    row_iter = iter(row_set)

    while True:
        i += 1
        try:
            row = row_iter.next()
            if not len(fields):
                fields = generate_field_spec(row)

            data = convert_row(row, fields, i)
            check_empty = set(data.values())
            if None in check_empty and len(check_empty) == 1:
                continue

            yield None, fields, data
        except StopIteration:
            return
        except Exception, e:
            # log.exception(e)
            yield e, fields, None


def validate_table(source):
    failed = 0
    for i, (exc, fields, row) in enumerate(parse_table(source)):
        if exc is not None:
            log.warning('Error at row %s: %s', i, unicode(exc))
            failed += 1

    log.info("Converted %s rows with %s columns.", i + 1, len(fields))
    source.meta['fields'] = fields
    source.meta['num_records'] = i + 1
    source.meta['num_failed'] = failed
    source.meta.save()
    return source


def load_table(source):
    for exc, fields, row in parse_table(source):
        if exc is None:
            yield row
