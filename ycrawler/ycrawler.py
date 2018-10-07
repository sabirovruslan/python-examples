import re

from spider.parser import ParserProtocol
from spider.spider import Spider


class ParserPostMainPage(ParserProtocol):

    def abstract_urls(self, html):
        urls = re.findall(self.rule, html)
        return urls



class YcombinatorSpider(Spider):
    parsers = [
        ParserPostMainPage(rule='item\?id=\d+')
    ]
    start_url = 'https://news.ycombinator.com/'
    base_url = 'https://news.ycombinator.com/'
    headers = {'User-Agent': 'Google Spider'}


if __name__ == '__main__':
    YcombinatorSpider.run()

