from StringIO import StringIO

from flask import Blueprint, render_template, request, redirect
from flask import Response, current_app, session
from webhelpers.feedgenerator import Rss201rev2Feed
from flask.ext.babel import gettext
from apikit import jsonify

from spendb.core import db, url_for
from spendb import auth
from spendb.model import Dataset
from spendb.assets import angular_templates
from spendb.validation.common import RESERVED_TERMS


blueprint = Blueprint('home', __name__)


@blueprint.route('/login')
@blueprint.route('/settings')
@blueprint.route('/accounts/<account>')
@blueprint.route('/docs/<path:page>')
@blueprint.route('/datasets')
@blueprint.route('/datasets/<path:path>')
@blueprint.route('/')
def index(*a, **kw):
    from flask.ext.babel import get_locale
    from spendb.views.context import etag_cache_keygen
    etag_cache_keygen(RESERVED_TERMS)
    locale = get_locale()
    data = {
        'current_language': locale.language,
        'url_for': url_for,
        'reserved_terms': RESERVED_TERMS,
        'templates': angular_templates(current_app),
        'site_url': url_for('home.index').rstrip('/'),
        'number_symbols_group': locale.number_symbols.get('group'),
        'number_symbols_decimal': locale.number_symbols.get('decimal'),
        'site_title': current_app.config.get('SITE_TITLE')
    }
    return render_template('layout.html', **data)


@blueprint.route('/set-locale', methods=['POST'])
def set_locale():
    locale = request.json.get('locale')

    if locale is not None:
        session['locale'] = locale
        session.modified = True
    return jsonify({'locale': locale})


@blueprint.route('/favicon.ico')
def favicon():
    return redirect('/static/img/favicon.ico', code=301)


@blueprint.route('/__ping__')
def ping():
    from spendb.tasks import ping
    ping.delay()
    return jsonify({
        'status': 'ok',
        'message': gettext("Sent ping!")
    })


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
            'link': '/datasets/%s' % feed_item.name,
            'description': feed_item.description,
            'author_name': ', '.join([person.fullname for person in
                                      feed_item.managers if
                                      person.fullname]),
        })
    desc = gettext('Recently created datasets on %(site_title)s',
                   site_title=current_app.config.get('SITE_TITLE'))
    feed = Rss201rev2Feed(gettext('Recently Created Datasets'),
                          url_for('home.index'), desc)
    for item in items:
        feed.add_item(**item)
    sio = StringIO()
    feed.write(sio, 'utf-8')
    return Response(sio.getvalue(), mimetype='application/xml')
