import logging
from datetime import datetime, date
from json import JSONEncoder

from flask import request, Response

log = logging.getLogger(__name__)


class AppEncoder(JSONEncoder):
    """ This encoder will serialize all entities that have a to_dict
    method by calling that method and serializing the result. """

    def default(self, obj):
        if hasattr(obj, 'as_dict'):
            return obj.as_dict()
        if hasattr(obj, 'to_dict'):
            return obj.to_dict()
        elif isinstance(obj, datetime):
            return obj.isoformat() + 'Z'
        elif isinstance(obj, date):
            return obj.isoformat()
        elif isinstance(obj, set):
            return [o for o in obj]
        return super(AppEncoder, self).default(obj)


def to_json(obj, encoder=None):
    if encoder is None:
        encoder = AppEncoder
    return encoder().encode(obj)


def jsonify(obj, status=200, headers=None, index=False, encoder=AppEncoder):
    """ Custom JSONificaton to support obj.as_dict protocol. """
    data = to_json(obj, encoder=encoder)
    if 'callback' in request.args:
        cb = request.args.get('callback')
        data = '%s && %s(%s)' % (cb, cb, data)
    return Response(data, headers=headers,
                    status=status,
                    mimetype='application/json')
