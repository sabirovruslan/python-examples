import os
from html import unescape

import aiohttp
from bs4 import BeautifulSoup

from spider.log import logger
from spider.request import fetch


class ItemProtocol:

    def __init__(self, html):
        raise NotImplementedError

    async def save(self, semaphore):
        raise NotImplementedError


class PostItem(ItemProtocol):
    STORE_DIR = '/usr/src/store'

    def __init__(self, html):
        soup = BeautifulSoup(html)
        self.post_id = soup.select_one('table.fatitem tr.athing').attrs['id']

        post_url = unescape(soup.select_one('a.storylink').attrs['href'])
        self.post_url = post_url

        self.comment_urls = []
        for selector in soup.select('div.comment a[rel=nofollow]'):
            _url = unescape(selector.attrs['href'])
            if _url in self.comment_urls:
                continue
            self.comment_urls.append(_url)

    async def save(self, semaphore):
        async with aiohttp.ClientSession() as session:
            html = await fetch(self.post_url, session, semaphore)
            if not html:
                logger.info(f'Page empty: {self.post_url}')
                return None
            self.write_to_file(html, self.create_file_name())

            comment_number = 1
            for url in self.comment_urls:
                html = await fetch(url, session, semaphore)
                if not html:
                    logger.info(f'Page empty: {self.post_url}')
                    return None
                self.write_to_file(html, self.create_file_name(prefix=f'comment_{comment_number}'))
                comment_number += 1

    def write_to_file(self, html, filename):
        try:
            with open(filename, "w") as f:
                f.write(html)
            logger.info(f'Write success: {filename}')
        except Exception as e:
            logger.error(f'error: {e}; file: {filename};')

    def create_file_name(self, prefix='post'):
        return f'{self._create_dirs(self.post_id)}/{prefix}_{self.post_id}.html'

    def _create_dirs(self, path: str):
        dirpath = os.path.join(self.STORE_DIR, path)
        os.makedirs(dirpath, exist_ok=True)
        return dirpath
