from flask import url_for

from spendb.core import db, data_manager
from spendb.etl import tasks
from spendb.model import Run
from spendb.lib.filters import readable_url

from spendb.tests.helpers import make_account
from spendb.tests.base import ControllerTestCase
from spendb.tests.etl.test_import_fixtures import import_fixture


from unittest import skip

@skip('Need to re-do run management')
class TestRunController(ControllerTestCase):

    def setUp(self):
        super(TestRunController, self).setUp()
        data_manager._index = None
        self.s3_mock.start()
        self.dataset, self.url = import_fixture('import_errors')

        source = tasks.extract_url(self.dataset, self.url)
        tasks.transform_source(self.dataset, source.name)
        tasks.load(self.dataset, source_name=source.name)

        self.run = db.session.query(Run).first()
        self.account = make_account()

    def tearDown(self):
        super(TestRunController, self).tearDown()
        self.s3_mock.stop()

    def test_view_run(self):
        response = self.client.get(url_for('run.view',
                                           dataset=self.dataset.name,
                                           id=self.run.id),
                                   query_string={'api_key': self.account.api_key})
        assert readable_url(self.url).encode('utf-8') in response.data

    def test_view_run_does_not_exist(self):
        response = self.client.get(url_for('run.view',
                                           dataset=self.source.dataset.name,
                                           id=47347893),
                                   query_string={'api_key': self.account.api_key})
        assert '404' in response.status, response.status
