from spendb import reference
from spendb.validation.dataset import valid_currency

from spendb.tests.base import TestCase


class TestCurrency(TestCase):
    def test_currency_constant(self):
        assert reference.CURRENCIES['EUR'] == ('Euro', True), \
            reference.CURRENCIES['EUR']
        assert reference.CURRENCIES['USD'] == ('US Dollar', True), \
            reference.CURRENCIES['USD']

    def test_currency_type_raises_invalid(self):
        assert valid_currency('not-a-code') is not True

    def test_currency_type_returns_valid(self):
        assert valid_currency('usd') is True
