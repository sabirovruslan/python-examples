import aiohttp
from abc import ABC

from spider.spider import Spider


class ParserProtocol(ABC):

    def __init__(self):
        pass

    async def task(self, spider: Spider, semaphore):
        async with aiohttp.ClientSession() as session:
            pass


    async def execute(self):
        pass
