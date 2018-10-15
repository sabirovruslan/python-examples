import multiprocessing
from abc import ABC
from concurrent.futures import ThreadPoolExecutor

import aiohttp
import asyncio

from spider.log import logger
from spider.parser import Parser
from spider.request import fetch_lock

try:
    import uvloop

    asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())
except ImportError:
    pass


class SpiderProtocol(ABC):
    parsers = []
    start_url = ''
    base_url = ''
    concurrency = 3
    sleep_time = 5.0
    headers = {}

    def __init__(self, item_cls):
        self.parsing_urls = []
        self.pre_parse_urls = asyncio.Queue()
        self.filter_urls = set()
        self.done_urls = []
        self.error_urls = []
        self.item_cls = item_cls
        self._semaphore = asyncio.Semaphore(self.concurrency)
        self._loop = asyncio.get_event_loop()

    def run(self):
        logger.info('Spider start run')
        try:
            self._loop.run_until_complete(asyncio.gather(
                self.init_parse(), self.task()
            ))
        except KeyboardInterrupt:
            for task in asyncio.Task.all_tasks():
                task.cancel()
            self._loop.stop()
        logger.info('Spider end run')

    async def init_parse(self):
        while True:
            async with aiohttp.ClientSession() as session:
                html = await fetch_lock(self.start_url, session, self._semaphore, headers=self.headers)
                self.parse(html)
                logger.info('Next iteration')
                await asyncio.sleep(self.sleep_time, loop=self._loop)

    def parse(self, html):
        for parser in self.parsers:
            for url in parser.parse_url(html, self.base_url):
                self.add(url)

    def add(self, url: str):
        if url in self.filter_urls:
            return None
        self.filter_urls.add(url)
        self.pre_parse_urls.put_nowait(url)

    async def task(self):
        async with aiohttp.ClientSession() as session:
            while True:
                url = await self.pre_parse_urls.get()
                self.parsing_urls.append(url)
                asyncio.ensure_future(self.execute_url(url, session))

    def is_running(self):
        return len(self.filter_urls) != len(self.done_urls)

    async def execute_url(self, url, session):
        html = await fetch_lock(url, session, self._semaphore, headers=self.headers)
        if not html:
            self.error_urls.append(url)
            self.pre_parse_urls.put_nowait(url)
            return None
        if url in self.error_urls:
            self.error_urls.remove(url)

        self.parsing_urls.remove(url)
        self.done_urls.append(url)

        item = self.item_cls(html, self._loop)
        await asyncio.ensure_future(item.save())
        logger.info('Parsed({}/{}): {}'.format(len(self.done_urls), len(self.filter_urls), url))


class YcombinatorSpider(SpiderProtocol):
    parsers = [
        Parser(rule='item\?id=\d+'),
    ]
    start_url = 'https://news.ycombinator.com/'
    base_url = 'https://news.ycombinator.com/'
    headers = {'User-Agent': 'Google Spider'}
