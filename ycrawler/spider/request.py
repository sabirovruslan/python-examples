from spider.log import logger


async def fetch_lock(url, session, semaphore, **kwargs):
    with (await semaphore):
        return await fetch(url, session, **kwargs)


async def fetch(url, session, **kwargs):
    async with session.get(url, headers=kwargs.get('headers', {})) as response:
        if response.status not in [200]:
            logger.error(f'Response error url:{url}; status:{response.status}')
            return None
        try:
            return await response.text()
        except Exception:
            return await response.read()
