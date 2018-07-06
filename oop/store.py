from abc import ABCMeta

from pymemcache.client import base


class CacheProviderInterface:
    __metaclass__ = ABCMeta

    def get(self, key):
        raise NotImplementedError

    def set(self, key, value, time=60):
        raise NotImplementedError


class MemcacheProvider(CacheProviderInterface):

    def __init__(self):
        self._client = base.Client(('localhost', 11211))

    def get(self, key):
        return self._client.get(key)

    def set(self, key, value, time=60):
        self._client.set(key, value, expire=time)


class Store:

    def __init__(self, cache_provider: CacheProviderInterface):
        self._cache = cache_provider

    def get(self, key):
        return self._cache.get(key)

    def cache_get(self, key):
        return self._cache.get(key)

    def cache_set(self, key, value, time=None):
        self._cache.set(key, value, time)
