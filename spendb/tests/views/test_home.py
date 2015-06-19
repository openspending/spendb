import re
import json
from flask import url_for

from spendb.core import db
from spendb.model.dataset import Dataset
from spendb.tests.base import ControllerTestCase
from spendb.tests.helpers import make_account, load_fixture


class TestHomeController(ControllerTestCase):

    def setUp(self):
        super(TestHomeController, self).setUp()
        self.dataset = load_fixture('cra')
        self.user = make_account('test')

    def test_index(self):
        response = self.client.get(url_for('home.index'))
        assert 'SpenDB' in response.data

    def test_locale(self):
        set_l = url_for('home.set_locale')
        data = json.dumps({'locale': 'en'})
        self.client.post(set_l, data=data,
                         headers={'Content-Type': 'application/json'})

    def test_feeds(self):
        # Anonymous user with one public dataset
        response = self.client.get(url_for('home.feed_rss'))
        assert 'application/xml' in response.content_type
        assert '<title>Recently Created Datasets</title>' in response.data
        assert '<item><title>Country Regional Analysis v2009' in response.data, response.data
        cra = Dataset.by_name('cra')
        cra.private = True
        db.session.add(cra)
        db.session.commit()

        # Anonymous user with one private dataset
        response = self.client.get(url_for('home.feed_rss'))
        assert 'application/xml' in response.content_type
        assert '<title>Recently Created Datasets</title>' in response.data
        assert '<item><title>Country Regional Analysis v2009' not in response.data

        # Logged in user with one public dataset
        cra.private = False
        db.session.add(cra)
        db.session.commit()
        response = self.client.get(url_for('home.feed_rss'),
                                   query_string={'api_key': self.user.api_key})
        assert 'application/xml' in response.content_type
        assert '<title>Recently Created Datasets</title>' in response.data
        assert '<item><title>Country Regional Analysis v2009' in response.data

        # Logged in user with one private dataset
        cra.private = True
        db.session.add(cra)
        db.session.commit()
        response = self.client.get(url_for('home.feed_rss'),
                                   query_string={'api_key': self.user.api_key})
        assert 'application/xml' in response.content_type
        assert '<title>Recently Created Datasets</title>' in response.data
        assert '<item><title>Country Regional Analysis v2009' not in response.data

        # Logged in admin user with one private dataset
        admin_user = make_account('admin')
        admin_user.admin = True
        db.session.add(admin_user)
        db.session.commit()
        response = self.client.get(url_for('home.feed_rss'),
                                   query_string={'api_key': admin_user.api_key})
        assert '<title>Recently Created Datasets</title>' in response.data
        assert '<item><title>Country Regional Analysis v2009' in response.data
        assert 'application/xml' in response.content_type

        response = self.client.get('/')
        norm = re.sub('\s+', ' ', response.data)
        assert ('<link rel="alternate" type="application/rss+xml" title="'
                'Latest Datasets on SpenDB"' in
                norm)
