import asyncio

try:
    import uvloop

    asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())
except ImportError:
    pass


class Spider:

    def __init__(self):
        pass

    def run(self):
        pass

    async def init_parse(self):
        pass