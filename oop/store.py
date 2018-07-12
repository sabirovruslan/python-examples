from abc import ABCMeta

from pymemcache.client.base import Client


class CacheAdapter:
    __metaclass__ = ABCMeta

    def get(self, key):
        raise NotImplementedError

    def set(self, key, value, time=0):
        raise NotImplementedError


class MemcacheAdapter(CacheAdapter):
    DEFAULT_TIMEOUT = 10

    def __init__(self, **kwargs):
        self.client = Client(
            server=(kwargs.get('address'), int(kwargs.get('port'))),
            connect_timeout=kwargs.get('connect_timeout', self.DEFAULT_TIMEOUT),
            timeout=kwargs.get('timeout', self.DEFAULT_TIMEOUT),
            ignore_exc=kwargs.get('ignore_exc', True)
        )

    def get(self, key):
        result = self.client.get(key)
        return result.decode('utf-8') if isinstance(result, bytes) else result

    def set(self, key, value, time=0):
        self.client.set(key, value, expire=time)


class Store:

    def __init__(self, cache_adapter: CacheAdapter, connect_attempts=None):
        self._cache = cache_adapter
        self._connect_attempts = connect_attempts or 1

    def get(self, key):
        return self._cache.get(key)

    def cache_get(self, key):
        attempts = 1
        while True:
            try:
                return self._cache.get(key)
            except Exception as e:
                if attempts != self._connect_attempts:
                    attempts += 1
                    continue
                raise

    def cache_set(self, key, value, time=0):
        attempts = 1
        while True:
            try:
                return self._cache.set(key, value, time)
            except Exception as e:
                if attempts != self._connect_attempts:
                    attempts += 1
                    continue
                raise
