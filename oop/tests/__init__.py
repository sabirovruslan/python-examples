import unittest

from tests.test_api import ApiTest
from tests.test_fields import CharFieldTest, ArgumentsFieldTest, EmailFieldTest, PhoneFieldTest, DateFieldTest, \
    BirthDayFieldTest, ClientIDsFieldTest, GenderFieldTest
from tests.test_server import MainHandlerTest
from tests.test_store import StoreTest


def suite():
    test_suite = unittest.TestSuite()
    test_suite.addTest(unittest.makeSuite(CharFieldTest))
    test_suite.addTest(unittest.makeSuite(ArgumentsFieldTest))
    test_suite.addTest(unittest.makeSuite(EmailFieldTest))
    test_suite.addTest(unittest.makeSuite(PhoneFieldTest))
    test_suite.addTest(unittest.makeSuite(DateFieldTest))
    test_suite.addTest(unittest.makeSuite(BirthDayFieldTest))
    test_suite.addTest(unittest.makeSuite(ClientIDsFieldTest))
    test_suite.addTest(unittest.makeSuite(GenderFieldTest))
    test_suite.addTest(unittest.makeSuite(ApiTest))
    test_suite.addTest(unittest.makeSuite(StoreTest))
    test_suite.addTest(unittest.makeSuite(MainHandlerTest))
    return test_suite


if __name__ == '__main__':
    runner = unittest.TextTestRunner()
    runner.run(suite())
