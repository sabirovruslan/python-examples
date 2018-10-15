import os
from html import unescape

import aiohttp
from bs4 import BeautifulSoup

from spider.log import logger
from spider.request import fetch


class PostItem:
    STORE_DIR = os.environ.get('STORE_DIR')

    def __init__(self, html, loop):
        soup = BeautifulSoup(html, features='html.parser')
        self.post_id = soup.select_one('table.fatitem tr.athing').attrs['id']
        self._loop = loop

        post_url = unescape(soup.select_one('a.storylink').attrs['href'])
        self.post_url = post_url

        self.comment_urls = []
        for selector in soup.select('div.comment a[rel=nofollow]'):
            _url = unescape(selector.attrs['href'])
            if _url in self.comment_urls:
                continue
            self.comment_urls.append(_url)

    async def save(self):
        async with aiohttp.ClientSession() as session:
            await self._save_page(self.post_url, session)

            comment_number = 1
            for url in self.comment_urls:
                await self._save_page(url, session, prefix=f'comment_{comment_number}')
                comment_number += 1

    async def _save_page(self, url, session, prefix='post'):
        try:
            html = await fetch(url, session)
            if not html:
                return None

            self._loop.run_in_executor(None, self._write_to_file, html, self._create_file_name(prefix))
        except Exception as e:
            logger.error(f'Save page: {self.post_url}; error: {e}')

    def _write_to_file(self, html, filename):
        try:
            if not isinstance(html, bytes):
                html = html.encode('utf-8')
            with open(filename, "wb") as f:
                f.write(html)
        except Exception as e:
            logger.error(f'error: {e}; file: {filename};')

    def _create_file_name(self, prefix):
        return f'{self._create_dirs(self.post_id)}/{prefix}_{self.post_id}.html'

    def _create_dirs(self, path: str):
        dirpath = os.path.join(self.STORE_DIR, path)
        os.makedirs(dirpath, exist_ok=True)
        return dirpath
