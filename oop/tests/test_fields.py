from unittest import TestCase

from api import CharField, ValidateFieldError, ArgumentsField, EmailField, PhoneField
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


class EmailFieldTest(TestCase):

    @cases(['test@test.ru', '21212@test.ru', 'email.test@test.ru'])
    def test_valid(self, value):
        field = EmailField()
        self.assertEqual(field.parse(value), value)

    @cases(['test.@.test.ru', '@test@.test.ru', 'test.test.ru', 'test@.ru'])
    def test_invalid(self, value):
        field = EmailField()
        with self.assertRaises(ValidateFieldError):
            field.parse(value)


class PhoneFieldTest(TestCase):

    @cases(['79000000000', 79000000001, 78000000000])
    def test_valid(self, value):
        field = PhoneField()
        self.assertEqual(field.parse(value), value)

    @cases(['7900000000', '89000000000', '+79000000000', 7800000000012])
    def test_invalid(self, value):
        field = PhoneField()
        with self.assertRaises(ValidateFieldError):
            field.parse(value)
