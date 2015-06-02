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

    def test_login(self):
        self.client.get(url_for('account.login'))

    def test_account_create_gives_api_key(self):
        account = make_account()
        assert len(account.api_key) == 36

    def test_settings(self):
        account = make_account()
        self.client.get(url_for('account.settings'),
                        query_string={'api_key': account.api_key})

    def test_after_login(self):
        self.client.get(url_for('account.login'))

    def test_after_logout(self):
        self.client.get(url_for('account.logout'))

    def test_trigger_reset_get(self):
        response = self.client.get(url_for('account.trigger_reset'))
        assert 'email address you used to register your account'\
            in response.data, response.data

    def test_trigger_reset_post_fail(self):
        response = self.client.post(url_for('account.trigger_reset'),
                                    data={'emailx': "foo@bar"})
        assert 'Please enter an email address' in response.data, response.data
        response = self.client.post(url_for('account.trigger_reset'),
                                    data={'email': "foo@bar"})
        assert 'No user is registered' in response.data, response.data

    def test_trigger_reset_post_ok(self):
        with mail.record_messages() as outbox:
            response = self.client.post(url_for('account.trigger_reset'),
                                        data={'email': self.user.email})
            assert '302' in response.status
            assert len(outbox) == 1, outbox
            assert self.user.email in outbox[0].recipients, \
                outbox[0].recipients

    def test_reset_get(self):
        response = self.client.get(url_for('account.do_reset',
                                   token='huhu',
                                   email='huhu@example.com'))
        assert '/login' in response.headers['location'], response.headers
        account = make_account()
        response = self.client.get(url_for('account.do_reset',
                                   token=account.token,
                                   email=account.email))
        assert '/settings' in response.headers['location'], response.headers

    def test_completion_access_check(self):
        response = self.client.get(url_for('account.complete'))
        obj = json.loads(response.data)
        assert u'You are not authorized to see that page' == \
            obj.get('errors'), response.data

    def test_distinct_json(self):
        test = make_account()
        response = self.client.get(url_for('account.complete'),
                                   query_string={'api_key': test.api_key})
        obj = response.json['results']
        assert 'fullname' in obj[0].keys(), obj
        assert len(obj) == 1, obj
        assert obj[0]['name'] == 'test', obj[0]

        response = self.client.get(url_for('account.complete'),
                                   query_string={'q': 'tes',
                                                 'api_key': test.api_key})
        obj = response.json['results']
        assert len(obj) == 1, obj

        response = self.client.get(url_for('account.complete'),
                                   query_string={'q': 'foo',
                                                 'api_key': test.api_key})
        obj = response.json['results']
        assert len(obj) == 0, obj

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

    def test_terms_check(self):
        """
        Test whether terms of use are present on the signup page (login) page
        and whether they are a required field.
        """

        # Get the login page
        response = self.client.get(url_for('account.login'))
        assert '200' in response.status, \
            'Error (status is not 200) while retrieving the login/signup page'

        # Check if user can send an input field for terms of use/privacy
        assert 'name="terms"' in response.data, \
            'Terms of use input field not present'

        # Check that not filling up the field throws a 'required' response
        # if the terms box is not in the post request (not checked)
        response = self.client.post(url_for('account.register'),
                                    data={'name': 'termschecker',
                                          'fullname': 'Term Checker',
                                          'email': 'termchecker@test.com',
                                          'password1': 'secret',
                                          'password2': 'secret'})
        assert 'name="terms"' in response.data, \
            'Terms of use checkbox not present after registering without tick'
        # Check if user is told it is required (this can be anywhere on the
        # page, and might not even be tied to terms of use checkbox but it
        # should be present nonetheless)
        assert 'Required' in response.data, \
            'User is not told that a field is "Required"'

        # Check that terms input field is not present after a successful
        # register
        response = self.client.post(url_for('account.register'),
                                    data={'name': 'termschecker',
                                          'fullname': 'Term Checker',
                                          'email': 'termchecker@test.com',
                                          'password1': 'secret',
                                          'password2': 'secret',
                                          'terms': True})
        assert 'name="terms"' not in response.data, \
            'Terms of use checkbox is present even after a successful register'
