import unittest

from tests.test_fields import FieldTest


def suite():
    test_suite = unittest.TestSuite()
    test_suite.addTest(unittest.makeSuite(FieldTest))
    return test_suite


if __name__ == '__main__':
    runner = unittest.TextTestRunner()
    runner.run(suite())
