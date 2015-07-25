# -*- coding: utf-8 -*-
""" Helper functions """
from flask import request
from apikit import obj_or_404

from spendb.auth import require
from spendb.model import Dataset


def get_dataset(name):
    dataset = obj_or_404(Dataset.by_name(name))
    require.dataset.read(dataset)
    return dataset


def get_page(param='page'):
    try:
        return int(request.args.get(param))
    except:
        return 1
