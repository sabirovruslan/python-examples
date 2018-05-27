from abc import ABCMeta

from core.config import Config
from core.parser_dir import ParserDir
from core.reports import HtmlReport, Report


class LogAnalyzer:
    __metaclass__ = ABCMeta

    def __init__(self, config:Config, report:Report=None):
        self._config = config
        self._parser = ParserDir(self._config.get('LOG_DIR'))
        self._report = report or HtmlReport()

    def analyze(self):
        raise NotImplementedError


class NginxLogAnalyzer(LogAnalyzer):

    _log_file = None

    def analyze(self):
        self._parser.run()
        self._parser.get_last_path_by_date()



    def get_info(self):
        pass
