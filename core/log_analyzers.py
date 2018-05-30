import collections
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

    def __init__(self, config:Config, report:ReportAbstract=None):
        self._config = config
        self._parser_dir = ParserDir(self._config.get('LOG_DIR'))
        self._report = report or HtmlReport(self._config.get('REPORT_DIR'))
        self._log_file = None

    def analyze(self):
        self._parser_dir.run()
        self._log_file = LogFile(self._parser_dir.get_last_path_by_date())
        self._report.init_template(self.parse_date_from_log_file())

        if self._report.is_exist():
            print('Лог уже проанализирован {}'.format(self._report.get_path()))
            return

        print('Старт анализа: {}'.format(self._log_file.get_path()))
        result = collections.defaultdict(list)
        total_count = total_time = 0
        for line in self._log_file.read():
            parsed_line = self.parse_line(line)
            if parsed_line:
                total_count += 1
                total_time += parsed_line['request_time']
                result[parsed_line['request_url']].append(parsed_line['request_time'])
        if total_count > 0 and total_time > 0:
            result = self.prepare_data_for_report(result, total_count, total_time)
            self._report.save(result)
            print('Анализ завершен: {}'.format(self._report.get_path()))
        else:
            print('Данные журнала пусты или имеют неверные данные')

    def parse_date_from_log_file(self):
        match = reg_date(self._log_file.get_path())
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

        return report_data[:self._config.get('REPORT_SIZE')]

    @staticmethod
    def median(data):
        data = sorted(data)
        n = len(data)
        if n == 0:
            return 0
        elif n % 2 == 1:
            return data[n // 2]
        return (data[(n + 1) // 2] + data[n // 2]) / 2
