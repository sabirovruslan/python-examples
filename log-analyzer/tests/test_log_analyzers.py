import os
from unittest import TestCase

from core.config import Config
from core.log_analyzers import NginxLogAnalyzer
from core.reports import HtmlReport


class LogAnalyzersTest(TestCase):

    def tearDown(self):
        path = './tests/testdata/reports/report-2017.06.30.html'
        if not os.path.isfile(path):
            return
        os.remove(path)

    def setUp(self):
        self.config_default = {
            "REPORT_SIZE": 1000,
            "REPORT_DIR": "./tests/testdata/reports",
            "LOG_DIR": "./tests/testdata/log"
        }
        self.config = Config(defaults=self.config_default)
        self.report = HtmlReport('./tests/testdata/reports/')
        self.report.init_template('2017.06.30')

    def test_analyze(self):
        self.assertEqual(self.report.is_exist(), False)
        nginx_log = NginxLogAnalyzer(config=self.config)
        nginx_log.analyze()
        self.assertEqual(self.report.is_exist(), True)


