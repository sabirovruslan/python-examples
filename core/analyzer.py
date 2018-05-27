from core.config import Config
from core.parser import Parser
from core.report import Report


class Analyzer:

    def __init__(self, config: Config):
        self.__config = config
        self.__parser = Parser()
        self.__report = Report()

    def run(self):
        pass

    def get_last_log_path(self):
        pass


    def get_info(self):
        pass
