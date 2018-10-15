from spider.item import PostItem
from spider.spider import YcombinatorSpider

if __name__ == '__main__':
    spider = YcombinatorSpider(item_cls=PostItem)
    spider.run()

