import json
import logging
from StringIO import StringIO
from urllib import urlencode

from webhelpers.feedgenerator import Rss201rev2Feed
from werkzeug.exceptions import BadRequest
from sqlalchemy.orm import aliased
from flask import Blueprint, render_template, request
from flask import Response, current_app
from flask.ext.login import current_user
from flask.ext.babel import gettext as _
from apikit import Pager

from spendb.core import db, url_for
from spendb.reference import COUNTRIES, LANGUAGES
from spendb.model import Dataset, DatasetLanguage, DatasetTerritory
from spendb import auth
from spendb.lib.helpers import get_dataset
from spendb.views.cache import etag_cache_keygen
from spendb.views.context import angular_templates

log = logging.getLogger(__name__)


blueprint = Blueprint('dataset', __name__)


@blueprint.route('/datasets')
def index():
    """ Get a list of all datasets along with territory, language, and
    category counts (amount of datasets for each). """
    q = Dataset.all_by_account(current_user, order=False)
    q = q.order_by(Dataset.updated_at.desc())

    # Filter by languages if they have been provided
    for language in request.args.getlist('languages'):
        l = aliased(DatasetLanguage)
        q = q.join(l, Dataset._languages)
        q = q.filter(l.code == language)

    # Filter by territories if they have been provided
    for territory in request.args.getlist('territories'):
        t = aliased(DatasetTerritory)
        q = q.join(t, Dataset._territories)
        q = q.filter(t.code == territory)

    # Return a list of languages as dicts with code, count, url and label
    languages = [{'code': code, 'count': count, 'label': LANGUAGES.get(code)}
                 for (code, count) in DatasetLanguage.dataset_counts(q)]

    territories = [{'code': code, 'count': count, 'label': COUNTRIES.get(code)}
                   for (code, count) in DatasetTerritory.dataset_counts(q)]

    pager = Pager(q)
    return render_template('dataset/index.html', pager=pager,
                           languages=languages, territories=territories)


@blueprint.route('/datasets/new')
def new():
    return render_template('angular.html', dataset=None,
                           templates=angular_templates(current_app))


@blueprint.route('/datasets/<dataset>')
def view(dataset):
    dataset = get_dataset(dataset)
    etag_cache_keygen(dataset.updated_at)
    managers = list(dataset.managers)
    return render_template('dataset/view.html', dataset=dataset,
                           managers=managers)


@blueprint.route('/datasets/<dataset>/admin')
@blueprint.route('/datasets/<dataset>/admin/metadata')
@blueprint.route('/datasets/<dataset>/admin/model')
@blueprint.route('/datasets/<dataset>/admin/runs/<run>')
def app(dataset, *a, **kw):
    dataset = get_dataset(dataset)
    etag_cache_keygen(dataset.updated_at)
    return render_template('angular.html', dataset=dataset,
                           templates=angular_templates(current_app))


@blueprint.route('/datasets.rss')
def feed_rss():
    q = db.session.query(Dataset)
    if not auth.account.is_admin():
        q = q.filter_by(private=False)
    feed_items = q.order_by(Dataset.created_at.desc()).limit(20)
    items = []
    for feed_item in feed_items:
        items.append({
            'title': feed_item.label,
            'pubdate': feed_item.updated_at,
            'link': url_for('dataset.view', dataset=feed_item.name),
            'description': feed_item.description,
            'author_name': ', '.join([person.fullname for person in
                                      feed_item.managers if
                                      person.fullname]),
        })
    desc = _('Recently created datasets on %(site_title)s',
             site_title=current_app.config.get('SITE_TITLE'))
    feed = Rss201rev2Feed(_('Recently Created Datasets'),
                          url_for('home.index'), desc)
    for item in items:
        feed.add_item(**item)
    sio = StringIO()
    feed.write(sio, 'utf-8')
    return Response(sio.getvalue(), mimetype='application/xml')
