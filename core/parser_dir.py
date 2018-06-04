import os
from glob import glob

from core.utils import reg_date


class ParserDir:

    def __init__(self, log_dir):
        if not os.path.isdir(log_dir):
            raise Exception('Дирректория не существует')
        self._log_dir = log_dir
        self._files = None

    def run(self):
        self._files = glob(self._log_dir + '/nginx-access-ui.log-*')

    def get_last_path_by_date(self):
        return max(self._files or [], key=lambda filename: reg_date(filename))
