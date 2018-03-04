from textblob import TextBlob


text = '''Great food. Went there after more than a year. Really wanted to have sausages today, and this place came to 
mind. I had the combo, and it was super filling. In addition to the Cevapi, Sudzukice, and chicken skewers, 
I like the bread as well. Their red pepper sauce is a bit mild for me mainly because I have a high tolerance for 
spiciness (but that's just a nit, and it only applies to me). '''

blob = TextBlob(text)
print(blob.noun_phrases)
for sentence in blob.sentences:
    print(sentence.sentiment, ' - ', sentence)


'''
import spacy

nlp = spacy.load('en_core_web_sm')
doc = nlp("displaCy uses CSS and JavaScript to show you how computers understand language")
for word in doc:
    # if word.dep_ in ('xcomp', 'ccomp'):
    print(word.dep_, word.text, ''.join(w.text_with_ws for w in word.subtree))
'''