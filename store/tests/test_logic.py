from django.test import TestCase

from store.logic import operations


class LogicTestCase(TestCase):

    def test_plus(self):
        result = operations(a=6, b=13)
        self.assertEqual(19, result)

    def test_minus(self):
        result = operations(a=6, b=13, c='-')
        self.assertEqual(-7, result)

    def test_multiply(self):
        result = operations(a=6, b=13, c='*')
        self.assertEqual(78, result)
