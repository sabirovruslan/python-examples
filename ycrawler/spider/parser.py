import asyncio
import re
from asyncio import Queue
from html import unescape
from urllib.parse import urljoin

import aiohttp
from abc import ABC

from spider.log import logger
from spider.request import fetch_lock


class ParserProtocol(ABC):

    def __init__(self, rule=None, item_cls=None):
        self.rule = rule
        self.parsing_urls = []
        self.pre_parse_urls = Queue()
        self.filter_urls = set()
        self.done_urls = []
        self.item_cls = item_cls

    async def task(self, spider, semaphore):
        async with aiohttp.ClientSession() as session:
            while spider.is_running():
                try:
                    url = await asyncio.wait_for(self.pre_parse_urls.get(), 5)
                    self.parsing_urls.append(url)
                    asyncio.ensure_future(self.execute_url(url, spider, session, semaphore))
                except asyncio.TimeoutError as e:
                    pass

    async def execute_url(self, url, spider, session, semaphore):
        html = await fetch_lock(url, session, semaphore, headers=spider.headers)
        if not html:
            spider.error_urls.append(url)
            self.pre_parse_urls.put_nowait(url)
            return None
        if url in spider.error_urls:
            spider.error_urls.remove(url)

        self.parsing_urls.remove(url)
        self.done_urls.append(url)

        if self.item_cls:
            item = self.item_cls(html)
            await item.save()
            logger.info('Parsed({}/{}): {}'.format(len(self.done_urls), len(self.filter_urls), url))
        else:
            logger.info('Followed({}/{}): {}'.format(len(self.done_urls), len(self.filter_urls), url))

    def parse_urls(self, html, base_url):
        if not html:
            return None
        for url in self.abstract_urls(html):
            url = unescape(url)
            if not re.match('(http|https)://', url):
                url = urljoin(base_url, url)
            self.add(url)

    def abstract_urls(self, html):
        raise NotImplementedError

    def add(self, url: str):
        if url in self.filter_urls:
            return None
        self.filter_urls.add(url)
        self.pre_parse_urls.put_nowait(url)


class Parser(ParserProtocol):

    def abstract_urls(self, html):
        urls = re.findall(self.rule, html)
        return urls
