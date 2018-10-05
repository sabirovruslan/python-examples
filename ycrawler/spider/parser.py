import asyncio
import re
from asyncio import Queue
from html import unescape
from urllib.parse import urljoin

import aiohttp
from abc import ABC

from spider.request import fetch
from spider.spider import Spider


class ParserProtocol(ABC):

    def __init__(self, rule=None):
        self.rule = rule
        self.parsing_urls = []
        self.pre_parse_urls = Queue()
        self.filter_urls = set()
        self.done_urls = []

    async def task(self, spider: Spider, semaphore):
        async with aiohttp.ClientSession() as session:
            while True:
                try:
                    url = await asyncio.wait_for(self.pre_parse_urls.get(), 5)
                    self.parsing_urls.append(url)
                    asyncio.ensure_future(self.execute_url(url, spider, session, semaphore))
                except asyncio.TimeoutError as e:
                    pass

    async def execute_url(self, url, spider, session, semaphore):
        html = await fetch(url, session, semaphore, headers=spider.headers)
        if not html:
            spider.error_urls.append(url)
            self.pre_parse_urls.put_nowait(url)
            return
        if url in spider.error_urls:
            spider.error_urls.remove(url)

        self.parsing_urls.remove(url)
        self.done_urls.append(url)

        # Todo parse

    def parse_url(self, html, base_url):
        if not html:
            return
        for url in self.abstract_urls(html):
            url = unescape(url)
            if not re.match('(http|https)://', url):
                url = urljoin(base_url, url)
            self.add(url)

    def abstract_urls(self, html):
        raise NotImplementedError

    def add(self, url: str):
        if url in self.filter_urls:
            return
        self.filter_urls.add(url)
        self.pre_parse_urls.put_nowait(url)
