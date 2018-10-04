import aiohttp
import asyncio

from spider.log import logger
from spider.request import fetch

try:
    import uvloop

    asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())
except ImportError:
    pass


class Spider:

    tasks = []
    start_url = 'news.ycombinator.com/'
    concurrency = 5
    interval = None

    @classmethod
    def run(cls):
        logger.info('Spider start run')
        loop = asyncio.get_event_loop()

        while True:
            try:
                semaphore = asyncio.Semaphore(cls.concurrency)
                loop.run_until_complete(cls.init_parse(semaphore))
            except KeyboardInterrupt:
                for task in asyncio.Task.all_tasks():
                    task.cancel()
                loop.stop()
                break
            finally:
                logger.info('Next iteration')
        logger.info('Spider end run')

    @classmethod
    async def init_parse(cls, semaphore):
        async with aiohttp.ClientSession() as session:
            html = await fetch(cls.start_url, semaphore)

    @classmethod
    def parse(cls, html):
        pass