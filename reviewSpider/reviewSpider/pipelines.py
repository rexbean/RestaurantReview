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
        if myGlobal.gName == '':
            myGlobal.gName = name
        if myGlobal.gName == name:
            myGlobal.reviewList.append(dict(item))
        elif myGlobal.gName != name:
            Util.writeJson(myGlobal.gName)
            myGlobal.reviewList[:] = []
            myGlobal.gName = name
        return item

    def close_spider(self, spider):
        Util.writeJson(myGlobal.gName)
