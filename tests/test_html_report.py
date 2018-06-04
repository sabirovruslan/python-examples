import os
from unittest import TestCase

from core.reports import HtmlReport


class ReportTest(TestCase):

    def tearDown(self):
        path = './tests/testdata/reports/report-2017.06.30.html'
        if not os.path.isfile(path):
            return
        os.remove(path)

    def test_save_file_exist(self):
        report = HtmlReport('./tests/testdata/reports/')
        report.init_template('2017.06.29')
        self.assertEqual(report.is_exist(), True)

    def test_save_file(self):
        report = HtmlReport('./tests/testdata/reports/')
        report.init_template('2017.06.30')
        self.assertEqual(report.is_exist(), False)
        report.save([])
        self.assertEqual(report.is_exist(), True)

    def test_read_no_file(self):
        with self.assertRaises(Exception):
            HtmlReport('test')
