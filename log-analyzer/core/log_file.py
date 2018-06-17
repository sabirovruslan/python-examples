import gzip
import os


class LogFile:

    def __init__(self, path):
        if not os.path.isfile(path):
            raise Exception('Файл не существует {}'.format(path))
        self.__path = path

    def get_path(self):
        return self.__path

    def read(self):
        file = self.__open()
        for line in file:
            yield line.decode('utf-8') if isinstance(line, bytes) else line
        file.close()

    def __open(self):
        return gzip.open(self.__path, 'rb') if self.__path.endswith(".gz") else open(self.__path)
