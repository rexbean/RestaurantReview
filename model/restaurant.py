import json
from model.review import Review
class Restaurant:
    reviews = []
    bigReview = ''
    path    = './reviewSpider/reviewSpider/data/'

    def __init__(self, name):
        self.name = name
        self.path = self.path + name +'.json'

    def setReviews(self):
        with open(self.path, 'r') as f:
            reviewDicts = json.load(f)
            for r in reviewDicts:
                review = Review(r['name'], r['index'], r['rating'], r['review'])
                # review.splitSentences()
                self.reviews.append(review)

    def concentate(self):
        for r in self.reviews:
            self.bigReview += r.review
        return self.bigReview


    def getAverageRating(self):
        sumRating = 0.0
        for r in self.reviews:
            sumRating += r.rating
        average = sumRating/len(self.reviews)
        return average

    def printReviews(self):
        for r in self.reviews:
            print(r.getIndex())
