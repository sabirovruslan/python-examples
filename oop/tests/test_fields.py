from unittest import TestCase

from api import CharField, ValidateFieldError, Request
from tests.utils import cases


class CharFieldTest(TestCase):

    @cases(['test', 'c', '123', 'g@'])
    def test_valid(self, value):
        char_field = CharField()
        self.assertEqual(char_field.parse(value), value)

    @cases([212, 0, 1000000000000])
    def test_invalid(self, value):
        char_field = CharField()
        with self.assertRaises(ValidateFieldError):
            self.assertRaises(char_field.parse(value))
