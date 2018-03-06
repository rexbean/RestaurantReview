import json
from review import Review
class Restaurant:
    reviews = []
    path    = './reviewSpider/reviewSpider/data/'

    def __init__(self, name):
        self.name = name
        self.path = self.path + name +'.json'

    def setReviews(self):
        with open(self.path, 'r') as f:
            reviewDicts = json.load(f)
            for r in reviewDicts:
                review = Review(r['name'], r['index'], r['rating'], r['review'])
                review.splitSentences()
                self.reviews.append(review)

    def printReviews(self):
        for r in self.reviews:
            print(r.getIndex())
