#!/usr/bin/python
# -*- coding:utf-8 -*-

import scrapy
import subprocess
import json
from reviewSpider.items import RestaurantItem

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
        # for n in range(1,11):
        n=1
        restaurant  = RestaurantItem()

        rootPath    = '//*[@id="super-container"]/div/div[2]/div[1]/div/div[4]/ul[2]'

        titlePath   = './li['+ str(n) + ']/div/div[1]/div[1]/div/div[2]/h3/span/a/span//text()'
        urlPath     = './li['+ str(n) + ']/div/div[1]/div[1]/div/div[2]/h3/span/a/@href'

        rootPath    = response.xpath(rootPath)
        title       = rootPath.xpath(titlePath).extract_first()
        url         = rootPath.xpath(urlPath).extract_first()

        if title is not None and url is not None:
            title               = title.replace(u'\u2019',"'")
            restaurant['title'] = title
            url                 = 'https://www.yelp.com'+ url
            restaurant['url']   = url
            print(restaurant['title'])
            print(restaurant['url'])
            yield scrapy.Request(url, callback=self.parseReview)

    def parseReview(self, response):
        with open("./review.txt", "a") as file:
            nextUrl = response.xpath('//*[@rel="next"]/@href').extract_first()
            title = response.xpath('//title//text()').extract_first()

            file.write('=================='+title.encode("UTF8") + '========================')

            jsonPath    = '//*[@type="application/ld+json"]'
            jsonFile  = response.xpath(jsonPath+"//text()").extract_first()

            reviewJson = json.loads(jsonFile)

            for r in reviewJson['review']:
                rating = r['reviewRating']['ratingValue']
                review = r['description']
                review = review.replace(u'\u2019',"'")
                file.write(str(rating))
                file.write(review.encode("UTF8"))
                # print(rating)
                # print(review)

            if nextUrl is not None:
                yield scrapy.Request(nextUrl,callback=self.parseReview)
