import os
from unittest import TestCase

from store import Store, MemcacheAdapter
from tests.utils import cases


class StoreTest(TestCase):

    def test_check(self):
        self.assertEqual(1, 1)

    @cases(['value', 1234, ''])
    def test_cache_set(self, value):
        store = Store(MemcacheAdapter(
            address=os.environ['STORE_PORT_11211_TCP_ADDR'],
            port=os.environ['STORE_PORT_11211_TCP_PORT']
        ))
        store.cache_set('test_cache_set', value)
        self.assertNotEqual(store.cache_get('test_cache_set'), None)

    @cases(['4321', 'key', 'test'])
    def test_cache_get_empty(self, key):
        store = Store(MemcacheAdapter(
            address=os.environ['STORE_PORT_11211_TCP_ADDR'],
            port=os.environ['STORE_PORT_11211_TCP_PORT']
        ))
        self.assertEqual(store.cache_get(key), None)

    def test_cache_set_error_connect(self):
        store = Store(MemcacheAdapter(
            address=os.environ['STORE_PORT_11211_TCP_ADDR'],
            port=8000
        ))
        with self.assertRaises(Exception):
            store.cache_set('error_set_key', 'test')

    def test_cache_get_error_connect(self):
        store = Store(MemcacheAdapter(
            address=os.environ['STORE_PORT_11211_TCP_ADDR'],
            port=8000,
            ignore_exc=False
        ))
        with self.assertRaises(Exception):
            store.cache_get('error_get_key',)

    @cases(['4321', 'key', 'test'])
    def test_cache_get_error_connect_and_ignore_exc(self, key):
        store = Store(MemcacheAdapter(
            address=os.environ['STORE_PORT_11211_TCP_ADDR'],
            port=8000
        ))
        self.assertEqual(store.cache_get(key), None)
