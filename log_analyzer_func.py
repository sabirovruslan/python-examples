#!/usr/bin/env python
# -*- coding: utf-8 -*-
import collections
import gzip
import json
import logging
import os
import re
from argparse import ArgumentParser
from glob import glob

from core.log_analyzers import NginxLogAnalyzer
from core.args import Args
from core.config import Config

config_default = {
    "REPORT_SIZE": 1000,
    "REPORT_DIR": "./reports",
    "LOG_DIR": "./log"
}

pattern = re.compile(
    (
        r''
        r'^\S+\s\S+\s{2}\S+\s\[.*?\]\s'
        r'\"\S+\s(\S+)\s\S+\"\s'
        r'\S+\s\S+\s.+?\s\".+?\"\s\S+\s\S+\s\S+\s'
        r'(\S+)'
    )
)


def main():
    try:
        init_config(config_default)
        logger = init_logging(config_default.get('LOGGING_DIR'))
    except Exception as e:
        print('Ошибка инициализации параметров: {}'.format(e))
        raise

    analyze(config_default, logger)


def init_config(config):
    parser = ArgumentParser()
    parser.add_argument('-c', '--config')
    args = parser.parse_args()
    if args.config:
        try:
            with open(args.config, mode='rb') as config_file:
                (key, val) = config_file.read().decode('utf-8').split('=')
                config[key.strip()] = val.strip()
        except IOError as e:
            e.strerror = 'Не удается загрузить файл конфигурации {}'.format(e.strerror)
            raise


def init_logging(filename=None):
    if filename and not os.path.isdir(filename):
        try:
            os.makedirs(filename)
        except OSError:
            return False
    logging.basicConfig(
        filename=filename,
        level=logging.INFO,
        format='[%(asctime)s] %(levelname).1s %(message)s'
    )
    return logging.getLogger('log_analyzers')


def analyze(config, logger):
    try:
        log_path = get_last_path_log(config.get('LOG_DIR'))
        report = os.path.join(
            config.get('REPORT_DIR'),
            'report-{}.html'.format(parse_date_from_log_file(log_path))
        )
    except Exception as e:
        logger.exception(e)
        return

    if os.path.exists(report):
        logger.info('Лог уже проанализирован {}'.format(report))
        return

    logger.info('Старт анализа: {}'.format(log_path))
    result = collections.defaultdict(list)
    total_count = 0
    total_time = 0
    error_count = 0
    for line in read_file(log_path):
        try:
            parsed_line = parse_line(line)
            if not parsed_line:
                continue
            total_count += 1
            total_time += parsed_line['request_time']
            result[parsed_line['request_url']].append(parsed_line['request_time'])
        except Exception:
            error_count += 1
    if not round(error_count * 100 / total_count) < config.get('PERCENT_ERROR', 0):
        result = prepare_data_for_report(result, total_count, total_time)
        save_report(report, result[:int(config.get('REPORT_SIZE'))])
    else:
        logger.error('Данные журнала пусты или имеют неверные данные')
    logger.info('Анализ завершен: {}'.format(report))


def get_last_path_log(log_dir):
    if not os.path.isdir(log_dir):
        raise Exception('Дирректория не существует: {}'.format(log_dir))
    files = glob(log_dir + '/nginx-access-ui.log-*')
    return max(files or [], key=lambda filename: reg_date(filename))


def parse_date_from_log_file(filename):
    match = reg_date(filename)
    return '{}.{}.{}'.format(match[:4], match[4:6], match[6:])


def read_file(log_path):
    file = gzip.open(log_path, 'rb') if log_path.endswith(".gz") else open(log_path)
    for line in file:
        yield line.decode('utf-8') if isinstance(line, bytes) else line
    file.close()


def parse_line(line):
    result = pattern.match(line)
    if not result:
        return None
    parsed_line = (dict(zip(('request_url', 'request_time'), result.groups())))
    parsed_line['request_time'] = float(parsed_line['request_time']) if parsed_line['request_time'] != '-' else 0
    return parsed_line


def prepare_data_for_report(data, total_count, total_time):
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
            'time_med': round(median(times), 3),
        })
    report_data.sort(key=lambda item: (item['time_perc'], item['time_sum']), reverse=True)

    return report_data


def median(data):
    data = sorted(data)
    n = len(data)
    if n == 0:
        return 0
    elif n % 2 == 1:
        return data[n // 2]
    return (data[(n + 1) // 2] + data[n // 2]) / 2


def save_report(filename, data):
    with open('./report.html', 'r') as f:
        file_data = f.read()
    file_data = file_data.replace('$table_json', json.dumps(data))
    with open(filename, 'w') as f:
        f.write(file_data)


def reg_date(value):
    return str(re.search('\d{4}\d{2}\d{2}', value).group())


if __name__ == "__main__":
    main()
