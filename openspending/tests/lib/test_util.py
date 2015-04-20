# -*- coding: utf-8 -*-
from openspending.lib import util
from openspending.tests.base import TestCase


class TestUtils(TestCase):

    def test_slugify(self):
        assert util.slugify(u'foo') == 'foo'
        assert util.slugify(u'fóo') == 'foo'
        assert util.slugify(u'fóo&bañ') == 'foo-ban'

    def test_hash_values(self):
        hash_value = util.hash_values([u'fóo&bañ'])
        assert hash_value == 'a2a4c050e75206e5fe84dbb7fe525c5dde8c848d'
