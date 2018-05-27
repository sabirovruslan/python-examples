import unittest

from tests.test_config import ConfigTest


def suite():
    test_suite = unittest.TestSuite()
    test_suite.addTest(unittest.makeSuite(ConfigTest))
    return test_suite


if __name__ == '__main__':
    runner = unittest.TextTestRunner()
    runner.run(suite())
