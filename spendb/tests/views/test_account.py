import json
import urllib2

from flask import url_for, current_app

from spendb.core import db, mail
from spendb.model.account import Account
from spendb.tests.base import ControllerTestCase
from spendb.tests.helpers import make_account, load_fixture


class TestAccountController(ControllerTestCase):

    def setUp(self):
        super(TestAccountController, self).setUp()

        # Create test user
        self.user = make_account('test')

    def test_settings(self):
        account = make_account()
        self.client.get(url_for('account.settings'),
                        query_string={'api_key': account.api_key})

    def test_dashboard_not_logged_in(self):
        response = self.client.get(url_for('account.dashboard'))
        assert '403' in response.status, response.status

    def test_dashboard(self):
        test = make_account('test')
        cra = load_fixture('cra', manager=test)
        response = self.client.get(url_for('account.dashboard'),
                                   query_string={'api_key': test.api_key})
        assert '200' in response.status, response.status
        assert unicode(cra.label) in response.data.decode('utf-8'), [response.data]

    def test_profile(self):
        """
        Profile page test
        """

        # Create the test user account using default
        # username is test, fullname is 'Test User',
        # email is test@example.com and twitter handle is testuser
        test = make_account('test')

        # Get the user profile for an anonymous user
        response = self.client.get(url_for('account.profile', account='test'))

        assert '200' in response.status, \
            'Profile not successfully returned for anonymous user'
        assert 'Name' in response.data, \
            'Name heading is not in profile for anonymous user'
        assert 'Test User' in response.data, \
            'User fullname is not in profile for anonymous user'
        assert 'Username' in response.data, \
            'Username heading is not in profile for anonymous user'
        assert 'test' in response.data, \
            'Username is not in profile for anonymous user'
        assert 'Email' not in response.data, \
            'Email heading is in profile for anonymous user'
        assert 'test@example.com' not in response.data, \
            'Email of user is in profile for anonymous user'
        assert '@testuser' not in response.data, \
            'Twitter handle is in profile for anonymous user'

        # Display email and twitter handle for the user
        response = self.client.get(url_for('account.profile', account='test'),
                                   query_string={'api_key': test.api_key})

        assert '200' in response.status, \
            'Profile not successfully returned for user'
        assert 'Email' in response.data, \
            'Email heading is not in profile for the user'
        assert 'test@example.com' in response.data, \
            'Email of user is not in profile for the user'
        assert '@testuser' in response.data, \
            'Twitter handle of user is not in profile for the user'

        # Immitate that the user now makes email address and twitter handle
        # public to all
        test.public_email = True
        test.public_twitter = True
        db.session.add(test)
        db.session.commit()

        # Get the site as an anonymous user
        response = self.client.get(url_for('account.profile', account='test'))

        assert '200' in response.status, \
            'Profile with public contact info not returned to anonymous user'
        assert 'Email' in response.data, \
            'Public email heading not in profile for anonymous user'
        assert 'test@example.com' in response.data, \
            'Public email not in profile for anonymous user'
        assert '@testuser' in response.data, \
            'Public Twitter handle not in profile for anonymous user'

        # We take it back and hide the email and the twitter handle
        test.public_email = False
        test.public_twitter = False
        db.session.add(test)
        db.session.commit()

        # Create admin user
        admin_user = make_account('admin', 'Admin', 'admin@os.com')
        admin_user.admin = True
        db.session.add(admin_user)
        db.session.commit()

        # Display email for admins
        response = self.client.get(url_for('account.profile', account='test'),
                                   query_string={'api_key': admin_user.api_key})

        assert '200' in response.status, \
            'Profile not successfully returned for admins'
        assert 'Name' in response.data, \
            'Full name heading not in profile for admins'
        assert 'Test User' in response.data, \
            'Full name of user not in profile for admins'
        assert 'Username' in response.data, \
            'Username heading not in profile for admins'
        assert 'test' in response.data, \
            'Username of user not in profile for admins'
        assert 'Email' in response.data, \
            'Email heading not in profile for admins'
        assert 'test@example.com' in response.data, \
            'Email of user not in profile for admins'
        assert 'Twitter' in response.data, \
            'Twitter heading not in profile for admins'
        assert '@testuser' in response.data, \
            'Twitter handle of user not in profile for admins'

        # Do not display fullname if it's empty
        test.fullname = ''
        db.session.add(test)
        db.session.commit()

        response = self.client.get(url_for('account.profile', account='test'))

        assert '200' in response.status, \
            'Profile page not successfully returned without full name'
        assert 'Name' not in response.data, \
            'Name heading is in profile even though full name is empty'
        # Test if the information is missing or just the full name
        assert 'Username' in response.data, \
            'Username heading is not in profile when full name is empty'
        assert 'test' in response.data, \
            'Username for user is not in profile when full name is empty'

        # Do not display twitter handle if it's empty
        test.twitter_handle = None
        db.session.add(test)
        db.session.commit()

        response = self.client.get(url_for('account.profile', account='test'),
                                   query_string={'api_key': test.api_key})

        # Test if the other information is missing
        assert 'Username' in response.data, \
            'Username heading is not in profile when Twitter handle is empty'
        assert 'test' in response.data, \
            'Username for user is not in profile when Twitter handle is empty'
