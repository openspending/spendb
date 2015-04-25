# -*- coding: utf-8 -*-
""" Helper functions """
from flask import flash, request
from apikit import obj_or_404

from spendb.core import url_for
from spendb.auth import require
from spendb.model import Dataset


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
