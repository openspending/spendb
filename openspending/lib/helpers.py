# -*- coding: utf-8 -*-
""" Helper functions """
from flask import url_for as flask_url_for
from flask import flash, request
from apikit import obj_or_404

from openspending.auth import require
from openspending.model import Dataset


def url_for(endpoint, **kwargs):
    kwargs['_external'] = True
    return flask_url_for(endpoint, **kwargs)


def static_path(filename):
    return url_for('static', filename=filename)


def get_dataset(name):
    dataset = obj_or_404(Dataset.by_name(name))
    require.dataset.read(dataset)
    return dataset


def get_page(param='page'):
    try:
        return int(request.args.get(param))
    except:
        return 1


def flash_notice(message):
    return flash(message, 'notice')


def flash_error(message):
    return flash(message, 'error')


def flash_success(message):
    return flash(message, 'success')
