#!/usr/bin/python
# -*- coding:utf-8 -*-

import scrapy
import subprocess
import json
import myGlobal
from reviewSpider.items import RestaurantItem
from reviewSpider.items import ReviewspiderItem

from scrapy.selector import Selector
from scrapy.http import HtmlResponse


class YelpSpider(scrapy.Spider):

    name = "yelp"
    urls = []

    start_urls = [
        # search the account with keyword
        "https://www.yelp.com/search?find_desc=&find_near=santa-clara-university-santa-clara&ns=1"

    ]

    def parse(self, response):
        for n in range(1,11):
            restaurant  = RestaurantItem()

            rootPath    = '//*[@id="super-container"]/div/div[2]/div[1]/div/div[4]/ul[2]'

            namePath    = './li['+ str(n) + ']/div/div[1]/div[1]/div/div[2]/h3/span/a/span//text()'
            urlPath     = './li['+ str(n) + ']/div/div[1]/div[1]/div/div[2]/h3/span/a/@href'

            rootPath    = response.xpath(rootPath)
            name        = rootPath.xpath(namePath).extract_first()
            url         = rootPath.xpath(urlPath).extract_first()

            if name is not None and url is not None:
                name                = name.replace(u'\u2019',"'")
                restaurant['name']  = name
                url                 = 'https://www.yelp.com'+ url
                restaurant['url']   = url
                meta = {}
                print(restaurant['name'])
                print(restaurant['url'])
                meta['name'] = name
                meta['index'] = 0
                print('=================='+name.encode("UTF8") + '========================')

                yield scrapy.Request(url, meta = meta, callback=self.parseReview)

    def parseReview(self, response):
        with open('./review-1.txt','a') as f:
            nextUrl = response.xpath('//*[@rel="next"]/@href').extract_first()
            title   = response.xpath('//title//text()').extract_first()

            name    = response.meta['name']
            index   = response.meta['index']

            # print('=================='+title.encode("UTF8") + '========================')

            jsonPath    = '//*[@type="application/ld+json"]'
            jsonFile  = response.xpath(jsonPath+"//text()").extract_first()

            reviewJson = json.loads(jsonFile)

            for r in reviewJson['review']:
                reviewItem = ReviewspiderItem()

                rating = r['reviewRating']['ratingValue']
                review = r['description']
                review = review.replace(u'\u2019',"'")
                reviewItem['name']      = name
                reviewItem['index']     = index
                reviewItem['rating']    = rating
                reviewItem['review']    = review

                index += 1
            if nextUrl is None:
                f.write('================'+name.encode('UTF8')+'================\n')
            else:
                f.write(name.encode('UTF8')+'\t'+ str(index) + '\t' + nextUrl.encode('UTF8')+'\n')
                # yield reviewItem

            if nextUrl is not None:
                response.meta['index']   = index
                yield scrapy.Request(nextUrl,meta = response.meta, callback=self.parseReview)
