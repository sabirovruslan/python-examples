import os
import requests
import logging

OPEN_WEATHER_URL = 'http://api.openweathermap.org/data/2.5/weather'
OPEN_WEATHER_API_KEY = os.environ.get('OPEN_WEATHER_API_KEY')
DEFAULT_ATTEMPTS_NUMBER = 5
DEFAULT_TIMEOUT = 0.5

logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] %(levelname).1s %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
    filename=os.environ.get('LOG_FILE')
)


def base_request(func):
    def wrapper(*args, **kwargs):
        timeout = DEFAULT_TIMEOUT
        attempts = 0
        while attempts < DEFAULT_ATTEMPTS_NUMBER:
            try:
                kwargs['timeout'] = timeout
                return func(**kwargs)
            except requests.exceptions.Timeout:
                logging.info('[{}] Attempt number {} has failed'.format(func.__name__, attempts))
                timeout += 1
                attempts += 1
                continue
            except requests.exceptions.RequestException as e:
                timeout += 1
                attempts += 1
                logging.exception(e)
                break
        else:
            return None

    return wrapper


@base_request
def get_ip_info(**kwargs):
    ip_value = kwargs.get('ip_value', None)
    if ip_value:
        url = 'https://ipinfo.io/{}/json'.format(ip_value)
    else:
        url = 'https://ipinfo.io/json'
    response = requests.get(url, timeout=1)
    return response.json()


@base_request
def get_weather_info(**kwargs):
    coords = kwargs.get('coords', None)
    timeout = kwargs.get('timeout', DEFAULT_TIMEOUT)
    if coords:
        response = requests.get(OPEN_WEATHER_URL, params={
            'lat': coords[0], 'lon': coords[1],
            'appid': OPEN_WEATHER_API_KEY
        }, timeout=timeout)
        return response.json()
    return None


def application(env, start_response):
    ip_info = None
    start_response('200 OK', [('Content-Type', 'application/json')])
    url_parameters = env.get('REQUEST_URI').split('/')
    url_parameters.remove('')
    if 'ip2w' in url_parameters:
        ip_info = get_ip_info(ip_value=url_parameters[-1])
    if ip_info:
        lat, long = ip_info.get('loc').split(',')
        weather = get_weather_info(coords=(float(lat), float(long)))
        if weather:
            return weather
        else:
            return {'error': 'Weather data is empty'}
    else:
        logging.warning('IP data is empty')
        return {'error': 'IP data is empty'}
