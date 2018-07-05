from unittest import TestCase

from api import CharField, ValidateFieldError, Request, ArgumentsField
from tests.utils import cases


class CharFieldTest(TestCase):

    @cases(['test', 'c', '123', 'g@'])
    def test_valid(self, value):
        field = CharField()
        self.assertEqual(field.parse(value), value)

    @cases([212, 0, 1000000000000])
    def test_invalid(self, value):
        field = CharField()
        with self.assertRaises(ValidateFieldError):
            field.parse(value)


class ArgumentsFieldTest(TestCase):

    @cases([{}, {'request': 212}])
    def test_valid(self, value):
        field = ArgumentsField()
        self.assertEqual(field.parse(value), value)

    @cases([[], 'dict', 2122])
    def test_invalid(self, value):
        field = ArgumentsField()
        with self.assertRaises(ValidateFieldError):
            field.parse(value)
