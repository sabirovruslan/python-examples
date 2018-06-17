#!/usr/bin/env python
# -*- coding: utf-8 -*-

from core.log_analyzers import NginxLogAnalyzer
from core.args import Args
from core.config import Config

config_default = {
    "REPORT_SIZE": 1000,
    "REPORT_DIR": "./reports",
    "LOG_DIR": "./log"
}


def main():
    config = __init_config()
    nginx_log = NginxLogAnalyzer(config=config)
    nginx_log.analyze()


def __init_config() -> Config:
    args = Args()
    config = Config(defaults=config_default)
    if args.config:
        config.from_file(args.config)
    return config


if __name__ == "__main__":
    main()
