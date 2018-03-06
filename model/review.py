from nltk.tokenize import sent_tokenize
class Review:
    name = ''
    index = 0
    rating = 0
    review = ''
    sentences = []
    def __init__(self, name, index, rating, review):
        self.name = name
        self.index = index
        self.rating = rating
        self.review = review

    def splitSentences(self):
        sentences = sent_tokenize(self.review)
        for s in sentences:
            s = s.strip()
            print(s)

    def setName(self, name):
        self.name = name

    def setIndex(self, index):
        self.index = index

    def setRating(self, rating):
        self.rating = rating

    def setReview(self, review):
        self.review = review

    def getName(self):
        return self.name

    def getIndex(self):
        return self.index

    def getRating(self):
        return self.rating

    def getReview(self):
        return self.review
