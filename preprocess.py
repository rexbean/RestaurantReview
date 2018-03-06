import json
from model.restaurant import Restaurant

restaurantList = []
## reviews i
# load review in
def getJsonFromFile(name):
    restaurant = Restaurant(name)
    restaurant.setReviews()

    restaurantList.append(restaurant)

getJsonFromFile(str(0))

# get frequent using aprior for all reviews
    ## give a threshold for the support
    ## can get frequent phrases

# split with the '.'

    # remove Illegle unicode & stopwords without pronoun

    # POS tagger get none & none phrase

    # search frequent map to get the frequent feature

    # get infreqeunt

    # parse the sentence

    # get the adjective near the subject / object
