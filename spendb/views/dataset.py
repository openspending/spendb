import json
import logging
from StringIO import StringIO
from urllib import urlencode

from webhelpers.feedgenerator import Rss201rev2Feed
from werkzeug.exceptions import BadRequest
from flask import Blueprint, render_template, request
from flask import Response, current_app
from flask.ext.login import current_user
from flask.ext.babel import gettext as _
from apikit import jsonify

from spendb.core import db
from spendb.model import Dataset
from spendb.lib.paramparser import DatasetIndexParamParser
from spendb import auth
from spendb.lib.indices import cached_index
from spendb.lib.helpers import url_for, get_dataset
from spendb.lib.pagination import Page
from spendb.views.cache import etag_cache_keygen
from spendb.views.context import angular_templates

log = logging.getLogger(__name__)


blueprint = Blueprint('dataset', __name__)


@blueprint.route('/datasets')
@blueprint.route('/datasets.<fmt:format>')
def index(format='html'):
    """ Get a list of all datasets along with territory, language, and
    category counts (amount of datasets for each). """

    # Parse the request parameters to get them into the right format
    parser = DatasetIndexParamParser(request.args)
    params, errors = parser.parse()
    if errors:
        concatenated_errors = ', '.join(errors)
        raise BadRequest(_('Parameter values not supported: %(errors)s',
                           errors=concatenated_errors))

    # We need to pop the page and pagesize parameters since they're not
    # used for the cache (we have to get all of the datasets to do the
    # language, territory, and category counts (these are then only used
    # for the html response)
    params.pop('page')
    pagesize = params.pop('pagesize')

    # Get cached indices (this will also generate them if there are no
    # cached results (the cache is invalidated when a dataset is published
    # or retracted
    account = current_user if current_user.is_authenticated() else None
    results = cached_index(account, **params)

    # Generate the ETag from the last modified timestamp of the first
    # dataset (since they are ordered in descending order by last
    # modified). It doesn't matter that this happens if it has (possibly)
    # generated the index (if not cached) since if it isn't cached then
    # the ETag is definitely modified. We wrap it in a try clause since
    # if there are no public datasets we'll get an index error.
    # We also don't set c._must_revalidate to True since we don't care
    # if the index needs a hard refresh
    try:
        first = results['datasets'][0]
        etag_cache_keygen(first['timestamps']['last_modified'])
    except IndexError:
        etag_cache_keygen(None)

    # Assign the results to template context variables
    language_options = results['languages']
    territory_options = results['territories']
    category_options = results['categories']

    # Create facet filters (so we can look at a single country,
    # language etc.)
    query = request.args.items()
    add_filter = lambda f, v: \
        '?' + urlencode(query +
                        [(f, v)] if (f, v) not in query else query)
    del_filter = lambda f, v: \
        '?' + urlencode([(k, x) for k, x in
                         query if (k, x) != (f, v)])

    # The page parameter we popped earlier is part of request.params but
    # we now know it was parsed. We have to send in request.params to
    # retain any parameters already supplied (filters)
    page = Page(results['datasets'], items_per_page=pagesize,
                item_count=len(results['datasets']),
                **dict(request.args.items()))
    return render_template('dataset/index.html', page=page,
                           query=query,
                           language_options=language_options,
                           territory_options=territory_options,
                           category_options=category_options,
                           add_filter=add_filter,
                           del_filter=del_filter)


@blueprint.route('/datasets/new')
def new():
    return render_template('dataset/new.html')


@blueprint.route('/datasets/<nodot:dataset>')
@blueprint.route('/datasets/<nodot:dataset>.<fmt:format>')
def view(dataset, format='html'):
    dataset = get_dataset(dataset)
    etag_cache_keygen(dataset.updated_at)
    managers = list(dataset.managers)
    return render_template('dataset/view.html', dataset=dataset,
                           managers=managers)


@blueprint.route('/datasets/<nodot:dataset>/manage', methods=['GET'])
@blueprint.route('/datasets/<nodot:dataset>/manage/meta', methods=['GET'])
@blueprint.route('/datasets/<nodot:dataset>/manage/model', methods=['GET'])
def manage(dataset):
    dataset = get_dataset(dataset)
    auth.require.dataset.update(dataset)
    return render_template('dataset/manage.html', dataset=dataset,
                           templates=angular_templates(current_app))


@blueprint.route('/datasets/<nodot:dataset>/model')
@blueprint.route('/datasets/<nodot:dataset>/model.<fmt:format>')
def model(dataset, format='json'):
    dataset = get_dataset(dataset)
    etag_cache_keygen(dataset.updated_at)
    model = dataset.model_data
    return jsonify(model)


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
