#!/usr/bin/env python
# -*- coding: utf-8 -*-
import gzip
import json
import logging
import os
import re
from argparse import ArgumentParser
from collections import defaultdict, namedtuple
from datetime import datetime

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

FileLog = namedtuple('FileLog', ['path', 'date'])


def main():
    args = get_args()
    init_config(config_default, args.config)
    init_logging(config_default.get('LOGGING_DIR'))
    analyze(config_default)


def get_args():
    parser = ArgumentParser()
    parser.add_argument('-c', '--config')
    return parser.parse_args()


def init_config(config, filename=None):
    if filename:
        try:
            with open(filename, mode='rb') as config_file:
                (key, val) = config_file.read().decode('utf-8').split('=')
                config[key.strip()] = val.strip()
        except:
            raise Exception('Can not load configuration file')


def init_logging(filename=None):
    if filename and not os.path.isdir(filename):
        os.makedirs(filename)
    logging.basicConfig(
        filename=filename,
        level=logging.INFO,
        format='[%(asctime)s] %(levelname).1s %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )


def analyze(config):
    try:
        file_log = get_last_log(config.get('LOG_DIR'))
        report_file = os.path.join(
            config.get('REPORT_DIR'),
            'report-{}.html'.format(file_log.date.strftime('%Y.%m.%d'))
        )
    except Exception as e:
        logging.exception(e)
        return

    if os.path.exists(report_file):
        logging.info('Лог уже проанализирован {}'.format(report_file))
        return

    logging.info('Старт анализа: {}'.format(file_log.path))
    report = defaultdict(list)
    try:
        for line in read_file(file_log.path, errors_limit=config.get('PERCENT_ERROR', 0)):
            report[line['request_url']].append(line['request_time'])
    except Exception as e:
        logging.exception(e)

    report = prepare_data_for_report(report)
    save_report(report_file, report[:int(config.get('REPORT_SIZE'))])

    logging.info('Анализ завершен: {}'.format(report_file))


def get_last_log(log_dir):
    if not os.path.isdir(log_dir):
        raise Exception('Directory does not exist: {}'.format(log_dir))

    file_log = None
    for filename in os.listdir(log_dir):
        match_result = re.match(r'^nginx-access-ui\.log-(?P<date>\d{8})(\.gz)?$', filename)
        if not match_result:
            continue
        date_value = datetime.strptime(match_result.groupdict()['date'], '%Y%m%d')
        if not file_log or date_value > file_log.date:
            file_log = FileLog(os.path.join(log_dir, filename), date_value)

    return file_log


def read_file(log_path, errors_limit):
    func = gzip.open if log_path.endswith(".gz") else open
    parse_lines = 0
    errors = 0
    with func(log_path, 'rb') as file:
        for line in file:
            line = line.decode('utf-8')
            report_line = parse_line(line)
            if not report_line:
                errors += 1
                continue
            parse_lines += 1
            yield report_line

    if round(errors * 100 / parse_lines) > errors_limit:
        raise Exception('The log data is empty or has incorrect data')


def parse_line(line):
    result = pattern.match(line)
    if not result:
        return None
    parsed_line = (dict(zip(('request_url', 'request_time'), result.groups())))
    parsed_line['request_time'] = float(parsed_line['request_time']) if parsed_line['request_time'] != '-' else 0
    return parsed_line


def prepare_data_for_report(data):
    report_data = []
    total_count = len(data.keys())
    total_time = sum([sum(times) for times in data.values()])
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


if __name__ == "__main__":
    main()
