import collections
import logging
import os
import re
from abc import ABCMeta

from core.config import Config
from core.log_file import LogFile
from core.parser_dir import ParserDir
from core.reports import HtmlReport, ReportAbstract
from core.utils import reg_date


class LogAnalyzer:
    __metaclass__ = ABCMeta

    def analyze(self):
        raise NotImplementedError


class NginxLogAnalyzer(LogAnalyzer):
    pattern = re.compile(
        (
            r''
            r'^\S+\s\S+\s{2}\S+\s\[.*?\]\s'
            r'\"\S+\s(\S+)\s\S+\"\s'
            r'\S+\s\S+\s.+?\s\".+?\"\s\S+\s\S+\s\S+\s'
            r'(\S+)'
        )
    )

    def __init__(self, config: Config, report: ReportAbstract = None):
        self.__config = config
        self.__logging = self.__init_logging()
        self.__log_file = None
        try:
            self.__parser_dir = ParserDir(self.__config.get('LOG_DIR'))
            self.__report = report or HtmlReport(self.__config.get('REPORT_DIR'))
        except Exception as e:
            self.__logging.exception(e)
            raise

    def __init_logging(self):
        folder = self.__create_log_folder()
        logging.basicConfig(
            filename=folder,
            level=logging.INFO,
            format='[%(asctime)s] %(levelname).1s %(message)s'
        )
        logger = logging.getLogger('log_analyzers')
        return logger

    def __create_log_folder(self):
        if not self.__config.get('LOGGING_DIR'):
            return False
        folder = os.path.dirname(self.__config.get('LOGGING_DIR'))
        if os.path.isdir(folder):
            return folder
        try:
            os.makedirs(folder)
        except OSError:
            return False
        return folder

    def analyze(self):
        try:
            self.__parser_dir.run()
            self.__log_file = LogFile(self.__parser_dir.get_last_path_by_date())
            self.__report.init_template(self.parse_date_from_log_file())
        except Exception as e:
            self.__logging.exception(e)
            raise

        if self.__report.is_exist():
            self.__logging.info('Лог уже проанализирован {}'.format(self.__report.get_path()))
            return

        self.__logging.info('Старт анализа: {}'.format(self.__log_file.get_path()))
        result = collections.defaultdict(list)
        total_count = 0
        total_time = 0
        error_count = 0
        for line in self.__log_file.read():
            try:
                parsed_line = self.parse_line(line)
                if not parsed_line:
                    continue
                total_count += 1
                total_time += parsed_line['request_time']
                result[parsed_line['request_url']].append(parsed_line['request_time'])
            except Exception:
                error_count += 1
        if not self.is_exceeded_percent_error(total_count, error_count):
            result = self.prepare_data_for_report(result, total_count, total_time)
            self.__report.save(result)
        else:
            self.__logging.error('Данные журнала пусты или имеют неверные данные')
        self.__logging.info('Анализ завершен: {}'.format(self.__report.get_path()))

    def parse_date_from_log_file(self):
        match = reg_date(self.__log_file.get_path())
        return '{}.{}.{}'.format(match[:4], match[4:6], match[6:])

    def parse_line(self, line):
        result = self.pattern.match(line)
        if not result:
            return None
        parsed_line = (dict(zip(('request_url', 'request_time'), result.groups())))
        parsed_line['request_time'] = float(parsed_line['request_time']) if parsed_line['request_time'] != '-' else 0
        return parsed_line

    def prepare_data_for_report(self, data, total_count, total_time):
        report_data = []
        one_count_percent = float(total_count / 100)
        one_time_percent = float(total_time / 100)

        for url, times in data.items():
            count = len(times)
            time_sum = sum(times)
            report_data.append({
                'url': url,
                'count': count,
                'count_perc': round(count / one_count_percent, 3),
                'time_sum': round(time_sum, 3),
                'time_perc': round(time_sum / one_time_percent, 3),
                'time_avg': round(time_sum / count, 3),
                'time_max': max(times),
                'time_med': round(self.median(times), 3),
            })
        report_data.sort(key=lambda item: (item['time_perc'], item['time_sum']), reverse=True)

        return report_data[:self.__config.get('REPORT_SIZE')]

    @staticmethod
    def median(data):
        data = sorted(data)
        n = len(data)
        if n == 0:
            return 0
        elif n % 2 == 1:
            return data[n // 2]
        return (data[(n + 1) // 2] + data[n // 2]) / 2

    def is_exceeded_percent_error(self, total: int, error: int):
        return round(error * 100 / total) < self.__config.get('PERCENT_ERROR', 0)
