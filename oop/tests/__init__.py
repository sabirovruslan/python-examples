import unittest

from tests.test_fields import CharFieldTest, ArgumentsFieldTest, EmailFieldTest


def suite():
    test_suite = unittest.TestSuite()
    test_suite.addTest(unittest.makeSuite(CharFieldTest))
    test_suite.addTest(unittest.makeSuite(ArgumentsFieldTest))
    test_suite.addTest(unittest.makeSuite(EmailFieldTest))
    return test_suite


if __name__ == '__main__':
    runner = unittest.TextTestRunner()
    runner.run(suite())
