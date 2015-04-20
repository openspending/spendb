import re
import json
import datetime

from flask import url_for
from flask.ext.babel import format_date

from spendb.core import db
from spendb.model.dataset import Dataset
from spendb.tests.base import ControllerTestCase
from spendb.tests.helpers import (make_account, load_fixture)


class TestDatasetController(ControllerTestCase):

    def setUp(self):
        super(TestDatasetController, self).setUp()
        self.dataset = load_fixture('cra')
        self.user = make_account('test')

    def test_index(self):
        response = self.client.get(url_for('dataset.index'))
        assert 'The database contains the following datasets' in response.data
        assert 'cra' in response.data

    def test_view_private(self):
        cra = Dataset.by_name('cra')
        cra.private = True
        db.session.commit()
        response = self.client.get(url_for('dataset.view', dataset='cra'))
        assert '403' in response.status
        assert 'Country Regional Analysis v2009' not in response.data, \
            "'Country Regional Analysis v2009' in response!"
        assert 'spendb_browser' not in response.data, \
            "'spendb_browser' in response!"

    def test_view_has_format_links(self):
        url_ = url_for('dataset.view', dataset='cra')
        response = self.client.get(url_)

        url_ = url_for('dataset.model', dataset='cra', format='json')

        assert url_ in response.data, \
            "Link to view page (JSON format) not in response!"

    def test_view_has_profile_links(self):
        self.dataset.managers.append(self.user)
        db.session.add(self.dataset)
        db.session.commit()
        response = self.client.get(url_for('dataset.view', dataset='cra'))
        profile_url = url_for('account.profile', name=self.user.name)
        assert profile_url in response.data
        assert self.user.fullname in response.data.decode('utf-8')

    def test_view_has_timestamps(self):
        """
        Test whether about page includes timestamps when dataset was created
        and when it was last updated
        """

        # Get the about page
        response = self.client.get(url_for('dataset.view', dataset='cra'))

        # Check assertions for timestamps
        assert 'Timestamps' in response.data, \
            'Timestamp header is not on about page'
        assert 'created on' in response.data, \
            'No line for "created on" on about page'
        assert 'last modified on' in response.data, \
            'No line for "last modified on" on about page'
        da = format_date(datetime.datetime.utcnow(), format='short')
        assert da in response.data.decode('utf-8'), \
            'Created (and update) timestamp is not on about page'

    def test_model_json(self):
        response = self.client.get(url_for('dataset.model',
                                           dataset='cra', format='json'))
        obj = json.loads(response.data)
        assert 'dataset' in obj.keys(), obj
        assert obj['dataset']['name'] == 'cra'
        assert obj['dataset']['label'] == 'Country Regional Analysis v2009'

    def test_new_form(self):
        response = self.client.get(url_for('dataset.new'),
                                   query_string={'api_key': self.user.api_key})
        assert "Import a dataset" in response.data

    def test_feeds(self):
        # Anonymous user with one public dataset
        response = self.client.get(url_for('dataset.feed_rss'))
        assert 'application/xml' in response.content_type
        assert '<title>Recently Created Datasets</title>' in response.data
        assert '<item><title>Country Regional Analysis v2009' in response.data
        cra = Dataset.by_name('cra')
        cra.private = True
        db.session.add(cra)
        db.session.commit()

        # Anonymous user with one private dataset
        response = self.client.get(url_for('dataset.feed_rss'))
        assert 'application/xml' in response.content_type
        assert '<title>Recently Created Datasets</title>' in response.data
        assert '<item><title>Country Regional Analysis v2009' not in response.data

        # Logged in user with one public dataset
        cra.private = False
        db.session.add(cra)
        db.session.commit()
        response = self.client.get(url_for('dataset.feed_rss'),
                                   query_string={'api_key': self.user.api_key})
        assert 'application/xml' in response.content_type
        assert '<title>Recently Created Datasets</title>' in response.data
        assert '<item><title>Country Regional Analysis v2009' in response.data

        # Logged in user with one private dataset
        cra.private = True
        db.session.add(cra)
        db.session.commit()
        response = self.client.get(url_for('dataset.feed_rss'),
                                   query_string={'api_key': self.user.api_key})
        assert 'application/xml' in response.content_type
        assert '<title>Recently Created Datasets</title>' in response.data
        assert '<item><title>Country Regional Analysis v2009' not in response.data

        # Logged in admin user with one private dataset
        admin_user = make_account('admin')
        admin_user.admin = True
        db.session.add(admin_user)
        db.session.commit()
        response = self.client.get(url_for('dataset.feed_rss'),
                                   query_string={'api_key': admin_user.api_key})
        assert '<title>Recently Created Datasets</title>' in response.data
        assert '<item><title>Country Regional Analysis v2009' in response.data
        assert 'application/xml' in response.content_type

        response = self.client.get(url_for('dataset.index'))
        norm = re.sub('\s+', ' ', response.data)
        assert ('<link rel="alternate" type="application/rss+xml" title="'
                'Latest Datasets on SpenDB"' in
                norm)
