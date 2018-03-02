#!/usr/bin/python
# -*- coding:utf-8 -*-

import json
from reviewSpider.spiders import myGlobal
class Util():
    @staticmethod
    def listToStr(strList):
        s = ''
        for c in strList:
            s += c
        return s

    @staticmethod
    def writeJson(name):
        print(name)
        path = './reviewSpider/data/'+name.encode('UTF8').replace(' ','').replace('\'','') + '.json'
        print(path)
        # Reading data back
        with open(path, 'wb') as f:
            json.dump(myGlobal.reviewList,f)

    @staticmethod
    def removeIllegal(s):
        s = s.replace( u'\u201c', u"\"").replace( u'\u201d', u"\"").replace( u'\u2026', u"...")
        s = s.replace( u'\u2013', u"-").replace( u'\u00a0', u" ").replace( u'\u00ae', u" ")
        s = s.replace( u'\u2014', u'-').replace( u'\u00e4', u'')
        s = s.replace( "?","")
        return s
