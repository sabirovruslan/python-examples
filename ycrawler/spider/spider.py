import asyncio

from spider.log import logger

try:
    import uvloop

    asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())
except ImportError:
    pass


class Spider:

    tasks = []
    base_url = ''
    concurrency = 5
    interval = None

    @classmethod
    def run(cls):
        logger.info('Spider start run')
        loop = asyncio.get_event_loop()

        while True:
            try:
                semaphore = asyncio.Semaphore(cls.concurrency)

            except KeyboardInterrupt:
                for task in asyncio.Task.all_tasks():
                    task.cancel()
                loop.stop()
                break
            finally:
                logger.info('Next iteration')
        logger.info('Spider end run')

    async def init_parse(self):
        pass