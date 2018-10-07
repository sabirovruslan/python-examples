

class ItemProtocol:

    def __init__(self, html):
        raise NotImplementedError

    async def save(self):
        raise NotImplementedError