from unittest import TestCase

from core.log_file import LogFile


class LogFileTest(TestCase):

    def test_read(self):
        log_file = LogFile('./tests/testdata/log/nginx-access-ui.log-20170630')
        count_lines = 0
        for line in log_file.read():
            self.assertIsInstance(line, str)
            count_lines +=1
        self.assertEqual(count_lines, 6)

    def test_read_empty(self):
        log_file = LogFile('./tests/testdata/log/nginx-access-ui.log-20170629')
        count_lines = 0
        for _ in log_file.read():
            count_lines +=1
        self.assertEqual(count_lines, 0)

    def test_read_broken_lines(self):
        log_file = LogFile('./tests/testdata/log/nginx-access-ui.log-20170628')
        count_lines = 0
        for _ in log_file.read():
            count_lines +=1
        self.assertEqual(count_lines, 9)

    def test_read_no_file(self):
        with self.assertRaises(Exception):
            LogFile('./tests/testdata/log/nginx-access-ui.log-2017')


