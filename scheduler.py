# -*- coding: utf-8 -*-

from crawler import Crawler
from db import Mongo
from setting import *


class Scheduler(object):
    def __init__(self):
        self.crawler = Crawler()
        self.db = Mongo(MONGO_DB)

    def main(self):
        self.db.add(MONGO_COLLECTION_URL, {'url': START_URL})
        while self.db.count(MONGO_COLLECTION_URL) > 0 and self.db.count(MONGO_COLLECTION_USERINFO) < 6:
            url = self.db.remove_one(MONGO_COLLECTION_URL)['url']
            userinfo, new_urls = self.crawler.main(url)
            self.db.add(MONGO_COLLECTION_USERINFO, userinfo)
            for new_url in new_urls:
                self.db.add(MONGO_COLLECTION_URL, {'url': new_url})


if __name__ == '__main__':
    scheduler = Scheduler()
    scheduler.main()