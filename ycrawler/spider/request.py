from spider.log import logger


async def fetch(url, session, semaphore, **kwargs):
    with (await semaphore):
        try:
            async with session.get(url, headers=kwargs.get('headers', {})) as response:
                if response.status not in [200]:
                    logger.error(f'Response error url:{url}; status:{response.status}')
                    return None
                data = await response.text()
                return data
        except Exception as e:
            logger.exception(f'Fetch: {e}')