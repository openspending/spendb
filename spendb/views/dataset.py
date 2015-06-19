import logging
from StringIO import StringIO

from webhelpers.feedgenerator import Rss201rev2Feed
from flask import Blueprint, render_template, Response, current_app
from flask.ext.babel import gettext as _

from spendb.core import db, url_for
from spendb.model import Dataset
from spendb import auth
from spendb.lib.helpers import get_dataset
from spendb.views.cache import etag_cache_keygen
from spendb.views.context import angular_templates
from spendb.views.api.dataset import query_index

log = logging.getLogger(__name__)


blueprint = Blueprint('dataset', __name__)


@blueprint.route('/datasets')
def index():
    """ Get a list of all datasets along with territory, language, and
    category counts (amount of datasets for each). """
    pager, languages, territories = query_index()
    etag_cache_keygen(pager.cache_keys())
    return render_template('dataset/index.html', pager=pager,
                           languages=languages, territories=territories)


@blueprint.route('/datasets/new')
@blueprint.route('/login')
def new():
    return render_template('angular.html',
                           templates=angular_templates(current_app))


@blueprint.route('/datasets/<dataset>')
def view(dataset):
    dataset = get_dataset(dataset)
    etag_cache_keygen(dataset.updated_at)
    managers = list(dataset.managers)
    return render_template('dataset/view.html', dataset=dataset,
                           managers=managers,
                           templates=angular_templates(current_app))


@blueprint.route('/datasets/<dataset>/admin/data')
@blueprint.route('/datasets/<dataset>/admin/metadata')
@blueprint.route('/datasets/<dataset>/admin/model')
@blueprint.route('/datasets/<dataset>/admin/runs/<run>')
def app(dataset, *a, **kw):
    dataset = get_dataset(dataset)
    etag_cache_keygen(dataset.updated_at)
    return render_template('dataset/angular.html', dataset=dataset,
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
