from openspending.reference import currency
from openspending.validation.model.dataset import valid_currency

from openspending.tests.base import TestCase


class TestCurrency(TestCase):
    def test_currency_constant(self):
        assert currency.CURRENCIES['EUR'] == ('Euro', True), \
            currency.CURRENCIES['EUR']
        assert currency.CURRENCIES['USD'] == ('US Dollar', True), \
            currency.CURRENCIES['USD']

    def test_currency_type_raises_invalid(self):
        assert valid_currency('not-a-code') is not True

    def test_currency_type_returns_valid(self):
        assert valid_currency('usd') is True

