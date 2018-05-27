#!/usr/bin/env python
# -*- coding: utf-8 -*-

from core.analyzer import Analyzer
from core.args import Args
from core.config import Config

config_default = {
    "REPORT_SIZE": 1000,
    "REPORT_DIR": "./reports",
    "LOG_DIR": "./log"
}

def main():
    config = __init_config()
    analyzer = Analyzer(config)
    analyzer.run()
    print(analyzer.get_info())


def __init_config() -> Config:
    args = Args()
    config = Config(defaults=config_default)
    if args.config:
        config.from_file(args.config)
    return config


if __name__ == "__main__":
    main()
