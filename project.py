from scrapy import cmdline

location = "santa Clara University" 
cmdline.execute("scrapy crawl yelp -a start_url='https://www.yelp.com/search?find_desc=&find_near=santa-clara-university-santa-clara&ns=1'".split())
