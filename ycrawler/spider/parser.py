import re
from abc import ABC
from html import unescape
from urllib.parse import urljoin


class ParserProtocol(ABC):

    def __init__(self, rule=None):
        self.rule = rule

    def parse_url(self, html, base_url):
        if not html:
            return None
        for url in self.abstract_urls(html):
            url = unescape(url)
            if not re.match('(http|https)://', url):
                url = urljoin(base_url, url)
            yield url

    def abstract_urls(self, html):
        raise NotImplementedError


class Parser(ParserProtocol):

    def abstract_urls(self, html):
        urls = re.findall(self.rule, html)
        return urls
