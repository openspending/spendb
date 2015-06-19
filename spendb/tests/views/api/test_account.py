import json

from flask import url_for

from spendb.core import db, mail
from spendb.tests.base import ControllerTestCase
from spendb.tests.helpers import make_account

JSON = {'content-type': 'application/json'}


class TestAccountApiController(ControllerTestCase):

    def setUp(self):
        super(TestAccountApiController, self).setUp()
        # Create test user
        self.user = make_account('test')

    def test_account_create_gives_api_key(self):
        account = make_account()
        assert len(account.api_key) == 36

    def test_trigger_reset_post_fail(self):
        response = self.client.post(url_for('account_api.trigger_reset'),
                                    data=json.dumps({'emailx': "foo@bar"}),
                                    headers=JSON)
        assert 'Please enter an email address' in response.data, response.data
        response = self.client.post(url_for('account_api.trigger_reset'),
                                    data=json.dumps({'email': "foo@bar"}),
                                    headers=JSON)
        assert 'No user is registered' in response.data, response.data

    def test_trigger_reset_post_ok(self):
        with mail.record_messages() as outbox:
            msg = json.dumps({'email': self.user.email})
            response = self.client.post(url_for('account_api.trigger_reset'),
                                        data=msg, headers=JSON)
            assert '200' in response.status, response.data
            assert len(outbox) == 1, outbox
            assert self.user.email in outbox[0].recipients, \
                outbox[0].recipients

    def test_reset_get(self):
        response = self.client.get(url_for('account_api.do_reset',
                                   token='huhu',
                                   email='huhu@example.com'))
        assert '/login' in response.headers['location'], response.headers
        account = make_account()
        response = self.client.get(url_for('account_api.do_reset',
                                   token=account.token,
                                   email=account.email))
        assert '/' in response.headers['location'], response.headers

    def test_completion_access_check(self):
        res = self.client.get(url_for('account_api.complete'))
        assert u'You are not authorized to see that page' in \
            res.json['message'], res.json

    def test_distinct_json(self):
        test = make_account()
        response = self.client.get(url_for('account_api.complete'),
                                   query_string={'api_key': test.api_key})
        obj = response.json['results']
        assert 'fullname' in obj[0].keys(), obj
        assert len(obj) == 1, obj
        assert obj[0]['name'] == 'test', obj[0]

        response = self.client.get(url_for('account_api.complete'),
                                   query_string={'q': 'tes',
                                                 'api_key': test.api_key})
        obj = response.json['results']
        assert len(obj) == 1, obj

        response = self.client.get(url_for('account_api.complete'),
                                   query_string={'q': 'foo',
                                                 'api_key': test.api_key})
        obj = response.json['results']
        assert len(obj) == 0, obj

    def test_profile(self):
        """
        Profile page test
        """

        # Create the test user account using default
        # username is test, fullname is 'Test User',
        # email is test@example.com and twitter handle is testuser
        test = make_account('test')

        # Get the user profile for an anonymous user
        response = self.client.get(url_for('account_api.view', account='test'))

        assert '200' in response.status, \
            'Profile not successfully returned for anonymous user'
        assert 'name' in response.data, \
            'Name heading is not in profile for anonymous user'
        assert 'Test User' in response.data, \
            'User fullname is not in profile for anonymous user'
        assert 'test' in response.data, \
            'Username is not in profile for anonymous user'
        assert 'email' not in response.data, \
            'Email heading is in profile for anonymous user'
        assert 'test@example.com' not in response.data, \
            'Email of user is in profile for anonymous user'
        assert '@testuser' not in response.data, \
            'Twitter handle is in profile for anonymous user'

        # Display email and twitter handle for the user
        response = self.client.get(url_for('account_api.view', account='test'),
                                   query_string={'api_key': test.api_key})
        print response.data
        assert '200' in response.status, \
            'Profile not successfully returned for user'
        assert 'email' in response.data, \
            'Email heading is not in profile for the user'
        assert 'test@example.com' in response.data, \
            'Email of user is not in profile for the user'
        assert 'testuser' in response.data, \
            'Twitter handle of user is not in profile for the user'

        # Immitate that the user now makes email address and twitter handle
        # public to all
        test.public_email = True
        test.public_twitter = True
        db.session.add(test)
        db.session.commit()

        # Get the site as an anonymous user
        response = self.client.get(url_for('account_api.view', account='test'))

        assert '200' in response.status, \
            'Profile with public contact info not returned to anonymous user'
        assert 'email' in response.data, \
            'Public email heading not in profile for anonymous user'
        assert 'test@example.com' in response.data, \
            'Public email not in profile for anonymous user'
        assert 'testuser' in response.data, \
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
        response = self.client.get(url_for('account_api.view', account='test'),
                                   query_string={'api_key': admin_user.api_key})

        assert '200' in response.status, \
            'Profile not successfully returned for admins'
        assert 'name' in response.data, \
            'Full name heading not in profile for admins'
        assert 'Test User' in response.data, \
            'Full name of user not in profile for admins'
        assert 'test' in response.data, \
            'Username of user not in profile for admins'
        assert 'email' in response.data, \
            'Email heading not in profile for admins'
        assert 'test@example.com' in response.data, \
            'Email of user not in profile for admins'
        assert 'twitter_handle' in response.data, \
            'Twitter heading not in profile for admins'
        assert 'testuser' in response.data, \
            'Twitter handle of user not in profile for admins'

    def test_terms_check(self):
        """
        Test whether terms of use are present on the signup page (login) page
        and whether they are a required field.
        """

        # Check that not filling up the field throws a 'required' response
        # if the terms box is not in the post request (not checked)
        response = self.client.post(url_for('account_api.register'),
                                    data={'name': 'termschecker',
                                          'fullname': 'Term Checker',
                                          'email': 'termchecker@test.com',
                                          'password1': 'secret',
                                          'password2': 'secret'})
        assert response.json['status'] == 400, response.data
        assert 'Required' in response.data, \
            'User is not told that a field is "Required"'

        # Check that terms input field is not present after a successful
        # register
        response = self.client.post(url_for('account_api.register'),
                                    data={'name': 'termschecker',
                                          'fullname': 'Term Checker',
                                          'email': 'termchecker@test.com',
                                          'password1': 'secret',
                                          'password2': 'secret',
                                          'terms': True})
        assert response.json['api_url'], response.data
        assert 'Required' not in response.data, \
            'Terms of use checkbox is present even after a successful register'
