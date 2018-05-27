#!/usr/bin/env python
# -*- coding: utf-8 -*-

import types
from argparse import ArgumentParser

config_default = {
    "REPORT_SIZE": 1000,
    "REPORT_DIR": "./reports",
    "LOG_DIR": "./log"
}


class CommandLineArgs:

    def __init__(self):
        parser = ArgumentParser()
        parser.add_argument('-c', '--config')

        self.args = parser.parse_args()

    def __getattr__(self, item):
        return getattr(self.args, item)


class Config(dict):

    def __init__(self, defaults=None):
        dict.__init__(self, defaults or {})

    def from_file(self, filename):
        config = types.ModuleType('config')
        config.__file__ = filename
        try:
            with open(filename, mode='rb') as config_file:
                exec(compile(config_file.read(), filename, 'exec'), config.__dict__)
        except IOError as e:
            e.strerror = 'Не удается загрузить файл конфигурации {}'.format(e.strerror)
            raise
        self.set_config(config)

    def set_config(self, config):
        for key in dir(config):
            if key.isupper():
                self[key] = getattr(config, key)


class Analyzer:
    pass


class Parser:
    pass


class Report:
    pass


def main():
    config = __init_config()

    print(config)


def __init_config() -> Config:
    args = CommandLineArgs()
    config = Config(defaults=config_default)
    if args.config:
        config.from_file(args.config)
    return config


if __name__ == "__main__":
    main()
