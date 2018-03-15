import json
import random
import re
import math
import spacy
from neuralcoref import Coref
from extractor import Extractor
from model.restaurant import Restaurant

restaurantList = []
## reviews i
# load review in
def norm(raw):
    return re.sub(r'\s+', ' ', str(raw))

def getJsonFromFile(name):
    restaurant = Restaurant(name)
    restaurant.setReviews()
    restaurantList.append(restaurant)
    for restaurant in restaurantList:

        extractor  = Extractor(restaurant.concentate())
        _summary = extractor.summary()
        for i, n in enumerate(sorted(_summary, key=lambda k: len(_summary[k][0]) + len(_summary[k][1]), reverse=True)):
            print(str(i + 1) + '.', '[' + n + ']', str(len(_summary[n][0])) + '/' + str(len(_summary[n][1])))

            print('\tpositive:')
            positive = _summary[n][0]
            if len(positive) > 3:
                positive = random.sample(positive, 3)
            for noun in positive:
                print('\t', norm(noun.sent))

            print('\tnegative:')
            negative = _summary[n][1]
            if len(negative) > 3:
                negative = random.sample(negative, 3)
            for noun in negative:
                print('\t', norm(noun.sent))
        break

def pronounResolution(doc):
    coref = Coref()
    clusters = coref.one_shot_coref(utterances=u"Their parents love them very much.", context=u"I kown a twins")

    resolved_utterance_text = coref.get_resolved_utterances()
    print(resolved_utterance_text)

if __name__ == '__main__':
    for i in range(0,10):
        getJsonFromFile(str(i))
