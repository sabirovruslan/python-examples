from abc import ABC


class ParserProtocol(ABC):

    def __init__(self):
        pass

    async def task(self):
        pass

    async def execute(self):
        pass
