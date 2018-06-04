from unittest import TestCase

from core.parser_dir import ParserDir


class ParseDirTest(TestCase):

    def test_scan(self):
        parser_dir = ParserDir('./tests/testdata/log')
        parser_dir.run()
        self.assertEqual(parser_dir.get_last_path_by_date(), './tests/testdata/log/nginx-access-ui.log-20170630')


    def test_scan_wrong_dir(self):
        parser_dir = ParserDir('./tests/log')
        with self.assertRaises(Exception):
            parser_dir.run()