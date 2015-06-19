from werkzeug.exceptions import HTTPException
from flask import request
from colander import Mapping
from apikit import jsonify


def handle_error(exc):
    status = 500
    title = exc.__class__.__name__
    message = unicode(exc)
    headers = {}
    if isinstance(exc, HTTPException):
        message = exc.get_description(request.environ)
        message = message.replace('<p>', '').replace('</p>', '')
        status = exc.code
        title = exc.name
        headers = exc.get_headers(request.environ)
    data = {
        'status': status,
        'title': title,
        'message': message
    }
    return jsonify(data, status=status, headers=headers)


def handle_invalid(exc):
    if isinstance(exc.node.typ, Mapping):
        exc.node.name = ''
    data = {
        'status': 400,
        'errors': exc.asdict()
    }
    return jsonify(data, status=400)
