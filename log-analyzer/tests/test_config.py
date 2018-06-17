from unittest import TestCase

from core.config import Config


class ConfigTest(TestCase):
    config_default = {
        "REPORT_SIZE": 1000,
        "REPORT_DIR": "./reports",
        "LOG_DIR": "./log"
    }

    def setUp(self):
        self.config = Config(defaults=self.config_default)

    def test_default(self):
        self.assertEqual(self.config['REPORT_SIZE'], self.config_default['REPORT_SIZE'])
        self.assertEqual(self.config['REPORT_DIR'], self.config_default['REPORT_DIR'])
        self.assertEqual(self.config['LOG_DIR'], self.config_default['LOG_DIR'])

    def test_from_file(self):
        self.config.from_file('./tests/testdata/config.cfg')

        self.assertEqual(self.config['REPORT_SIZE'], 1050)
        self.assertEqual(self.config['REPORT_DIR'], './test_reports')
        self.assertEqual(self.config['LOG_DIR'], './test_log')

    def test_partial_configuration_from_file(self):
        self.config.from_file('./tests/testdata/config_report_size.cfg')

        self.assertEqual(self.config['REPORT_SIZE'], 1050)
        self.assertEqual(self.config['REPORT_DIR'], self.config_default['REPORT_DIR'])
        self.assertEqual(self.config['LOG_DIR'], self.config_default['LOG_DIR'])

    def test_empty_from_file(self):
        self.config.from_file('./tests/testdata/config_empty.cfg')

        self.assertEqual(self.config['REPORT_SIZE'], self.config_default['REPORT_SIZE'])
        self.assertEqual(self.config['REPORT_DIR'], self.config_default['REPORT_DIR'])
        self.assertEqual(self.config['LOG_DIR'], self.config_default['LOG_DIR'])

    def test_not_exist_from_file(self):
        with self.assertRaises(Exception):
            self.config.from_file('./tests/testdata/config_test.cfg')