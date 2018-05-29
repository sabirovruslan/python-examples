import json
import os
from abc import ABCMeta


class ReportAbstract:
    __metaclass__ = ABCMeta

    def __init__(self, report_dir):
        self._report_dir = report_dir
        self._path = None

    def init_template(self, value):
        raise NotImplementedError

    def save(self, data):
        raise NotImplementedError

    def is_exist(self):
        return os.path.exists(self._path)

    def get_path(self):
        return self._path


class HtmlReport(ReportAbstract):

    def init_template(self, value):
        self._path = os.path.join(self._report_dir, 'report-{}.html'.format(value))

    def save(self, data):
        with open('./report.html', 'r') as f:
            file_data = f.read()
        file_data = file_data.replace('$table_json', json.dumps(data))
        with open(self._path, 'w') as f:
            f.write(file_data)
