import collections
import gzip
import logging
import multiprocessing
import os
import sys
import time
from datetime import timedelta
from glob import glob
from optparse import OptionParser

# brew install protobuf
# protoc  --python_out=. ./appsinstalled.proto
# pip install protobuf
from threading import Thread
# pip install python-memcached
import memcache

from appsinstalled_pb2 import UserApps

NORMAL_ERR_RATE = 0.01
AppsInstalled = collections.namedtuple('AppsInstalled', ['dev_type', 'dev_id', 'lat', 'lon', 'apps'])

TERMINATE = 'terminate'
DEFAULT_TIMEOUT = 3


def dot_rename(path):
    head, fn = os.path.split(path)
    # atomic in most cases
    os.rename(path, os.path.join(head, '.' + fn))


def parse_appsinstalled(line):
    line_parts = line.strip().split('\t')
    if len(line_parts) < 5:
        return
    dev_type, dev_id, lat, lon, raw_apps = line_parts
    if not dev_type or not dev_id:
        return
    try:
        apps = [int(a.strip()) for a in raw_apps.split(',')]
    except ValueError:
        apps = [int(a.strip()) for a in raw_apps.split(',') if a.isidigit()]
        logging.info(f'Not all user apps are digits: {line}')
    try:
        lat, lon = float(lat), float(lon)
    except ValueError:
        logging.info(f'Invalid geo coords: {line}')
    return AppsInstalled(dev_type, dev_id, lat, lon, apps)


def worker(filename, q, device_memc, options):
    start_time = time.time()
    if filename.endswith('.tsv.gz'):
        fd = gzip.open(filename)
    else:
        fd = open(filename)

    for line in fd:
        appsinstalled = parse_appsinstalled(line)
        memc_addr = device_memc.get(appsinstalled.dev_type)
        params_hash = {
            'appsinstalled': appsinstalled,
            'memc_addr': memc_addr,
            'dry': options.dry
        }
        q.put(params_hash)

    time_value = time.time() - start_time
    logging.info('WORKER EXECUTION: {}'.format(
        timedelta(seconds=time_value))
    )
    fd.close()


def listener(q, options):
    start_time = time.time()

    while True:
        item = q.get()
        logging.info(
            'LISTENER EXECUTION START {}'.format(start_time)
        )
        if item == TERMINATE:
            break
        memc_addr = item.get('memc_addr')
        appsinstalled = item.get('appsinstalled')
        dry = item.get('dry')
        ua = UserApps()
        ua.lat = appsinstalled.lat
        ua.lon = appsinstalled.lon
        key = f'{appsinstalled.dev_type}:{appsinstalled.dev_id}'
        ua.apps.extend(appsinstalled.apps)
        packed = ua.SerializeToString()

        try:
            if not dry:
                memc = memcache.Client(
                    [memc_addr], socket_timeout=DEFAULT_TIMEOUT)
                memc.set(key, packed)
                diff = time.time() - start_time
                logging.info(
                    'LISTENER EXECUTION END {}'.format(timedelta(seconds=diff))
                )
        except Exception as e:
            logging.exception('Cannot write to memc %s: %s' % (memc_addr, e))
            return False


def main(options):
    processed = errors = 0
    manager = multiprocessing.Manager()
    q = manager.Queue()
    pool = multiprocessing.Pool(multiprocessing.cpu_count())
    device_memc = {
        'idfa': options.idfa,
        'gaid': options.gaid,
        'adid': options.adid,
        'dvid': options.dvid,
    }
    files = glob(options.pattern)
    files.sort(reverse=True)
    jobs = []
    listeners = []

    for item in range(multiprocessing.cpu_count()):
        lstnr = Thread(target=listener, args=(q, options))
        listeners.append(lstnr)

    for item in files:
        job = pool.apply_async(worker, (item, q, device_memc, options))
        jobs.append(job)

    for lstnr in listeners:
        lstnr.start()

    for job in jobs:
        try:
            job.get(timeout=DEFAULT_TIMEOUT)
            processed += 1
        except Exception as e:
            logging.exception(e)
            errors += 1

    for lstnr in listeners:
        q.put(TERMINATE)
        lstnr.join()

    pool.close()

    if processed:
        err_rate = float(errors) / processed
    else:
        err_rate = 1

    if err_rate < NORMAL_ERR_RATE:
        logging.info(f'Acceptable error rate {err_rate}. Successfull load')
    else:
        logging.error(f'High error rate {err_rate} > {NORMAL_ERR_RATE}. Failed load')


if __name__ == '__main__':
    op = OptionParser()
    op.add_option('-t', '--test', action='store_true', default=False)
    op.add_option('-l', '--log', action='store', default=None)
    op.add_option('--dry', action='store_true', default=False)
    op.add_option(
        '--pattern', action='store', default='/data/appsinstalled/*.tsv.gz'
    )
    op.add_option('--idfa', action='store', default='127.0.0.1:33013')
    op.add_option('--gaid', action='store', default='127.0.0.1:33014')
    op.add_option('--adid', action='store', default='127.0.0.1:33015')
    op.add_option('--dvid', action='store', default='127.0.0.1:33016')
    (opts, args) = op.parse_args()
    level = logging.INFO if not opts.dry else logging.DEBUG
    logging.basicConfig(
        filename=opts.log, level=level,
        format='[%(asctime)s] %(levelname).1s %(message)s', datefmt='%Y.%m.%d %H:%M:%S')
    logging.info('Memc loader started with options: %s' % opts)
    try:
        main(opts)
    except Exception as e:
        logging.exception('Unexpected error: %s' % e)
        sys.exit(1)
