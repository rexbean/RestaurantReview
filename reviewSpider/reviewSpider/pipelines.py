# -*- coding: utf-8 -*-
from reviewSpider.spiders import myGlobal
from util.util import Util
# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html


class ReviewspiderPipeline(object):
    def process_item(self, item, spider):
        name = item['name']
        index = myGlobal.nameIndex[name]
        myGlobal.reviewList[index].append(dict(item))
        return item

    def close_spider(self, spider):
        for index, reviews in enumerate(myGlobal.reviewList):
            Util.writeJson(index, reviews)
