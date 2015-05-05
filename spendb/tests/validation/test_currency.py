from spendb import reference

from spendb.tests.base import TestCase


class TestCurrency(TestCase):
    def test_currency_constant(self):
        assert reference.CURRENCIES['EUR'] == ('Euro', True), \
            reference.CURRENCIES['EUR']
        assert reference.CURRENCIES['USD'] == ('US Dollar', True), \
            reference.CURRENCIES['USD']

    def test_currency_type_raises_invalid(self):
        assert 'not-a-code' not in reference.CURRENCIES

    def test_currency_type_returns_valid(self):
        assert 'USD' in reference.CURRENCIES
