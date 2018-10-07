from abc import ABC

import aiohttp
import asyncio

from spider.item import PostItem
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
    interval = None
    headers = {}
    error_urls = []
    sleep_time = 5.0

    @classmethod
    def run(cls):
        logger.info('Spider start run')
        loop = asyncio.get_event_loop()
        semaphore = asyncio.Semaphore(cls.concurrency)
        tasks = asyncio.wait([parser.task(cls, semaphore) for parser in cls.parsers])

        while True:
            try:
                loop.run_until_complete(cls.init_parse(semaphore, loop))
                loop.run_until_complete(tasks)
            except KeyboardInterrupt:
                for task in asyncio.Task.all_tasks():
                    task.cancel()
                loop.stop()
                break
            finally:
                logger.info('Next iteration')
        logger.info('Spider end run')

    @classmethod
    async def init_parse(cls, semaphore, loop):
        async with aiohttp.ClientSession() as session:
            html = await fetch_lock(cls.start_url, session, semaphore, headers=cls.headers)
            cls.parse(html)
            await asyncio.sleep(cls.sleep_time, loop=loop)

    @classmethod
    def parse(cls, html):
        for parser in cls.parsers:
            parser.parse_urls(html, cls.base_url)

    @classmethod
    def is_running(cls):
        is_running = False
        for parser in cls.parsers:
            if len(parser.filter_urls) != len(parser.done_urls):
                is_running = True
        return is_running


class YcombinatorSpider(SpiderProtocol):
    parsers = [
        Parser(rule='item\?id=\d+', item_cls=PostItem),
    ]
    start_url = 'https://news.ycombinator.com/'
    base_url = 'https://news.ycombinator.com/'
    headers = {'User-Agent': 'Google Spider'}
