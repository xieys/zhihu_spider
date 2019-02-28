# -*- coding: utf-8 -*-

import pymongo


class Mongo(object):
    def __init__(self, db):
        self.client = pymongo.MongoClient(host='localhost', port=27017)
        self.db = self.client[db]

    def add(self, collection, data):
        """
        添加数据到
        :param collection:数据库文档
        :param data: 数据
        :return:
        """
        if self.find(collection, data).count() == 0 and data is not None:
            self.db[collection].insert(data)
            print("保存{}到{}数据库集合成功。".format(data, collection))

    def find(self, collection, data):
        """
        查询数据
        :param collection:数据库文档
        :param data: 数据
        :return:
        """
        result = self.db[collection].find(data)
        return result

    def count(self, collection):
        """
        查询数据库大小
        :param collection:
        :return:
        """
        return self.db[collection].count()

    def remove_one(self, collection):
        """
        删除数据库集合中的一条数据
        :param collection:
        :return:
        """
        url = self.db[collection].find_one_and_delete({})
        return url
