import unittest

from tests.test_config import ConfigTest
from tests.test_parser_dir import ParseDirTest


def suite():
    test_suite = unittest.TestSuite()
    test_suite.addTest(unittest.makeSuite(ConfigTest))
    test_suite.addTest(unittest.makeSuite(ParseDirTest))
    return test_suite


if __name__ == '__main__':
    runner = unittest.TextTestRunner()
    runner.run(suite())
