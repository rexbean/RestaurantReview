import json
import re
from collections import defaultdict
import spacy


class FeatureExtractor:
    nlp = spacy.load('en')  # en_core_web_lg

    def __init__(self, text):
        self.raw = text
        self.doc = self.nlp(text)

    def nouns(self):
        for span in self.doc.noun_chunks:
            # TODO: subject/object filter
            for i, token in reversed(list(enumerate(span))):
                # CD=cardinal number, DT=determiner, PRP=pronoun(personal), PRP$=pronoun(possessive)
                if token.tag_ in ('CD', 'DT', 'PRP', 'PRP$') or token.is_stop:
                    if i < len(span) - 1:
                        yield span[i + 1:]
                    break
                elif i == 0:
                    yield span

    def freqs(self):
        freqs = defaultdict(list)
        for noun in self.nouns():
            freqs[normalize(noun.lemma_)].append(noun)
        # TODO: fuzzy matching
        # define an itemset as frequent if it appears in more than 1% of the review sentences
        threshold = max(2, int(len(list(self.doc.sents)) * 0.01))
        return {noun: freqs[noun] for noun in freqs if len(freqs[noun]) >= threshold}


def normalize(raw):
    return re.sub(r'\s+', ' ', str(raw))


if __name__ == "__main__":
    with open('reviewSpider/reviewSpider/data/IkesLoveandSandwiches.json') as file:
        _txt = '\n\n'.join(item['review'] for item in json.load(file))
    _fe = FeatureExtractor(_txt)

    # for noun in _fe.nouns():
    #     print(normalize(noun.lemma_), ' - ', normalize(noun.sent))
    #     for word in noun:
    #         # normalize(''.join(w.text_with_ws for w in word.subtree))
    #         print('\t', word.text, ':', word.pos_, word.tag_, word.dep_)

    _freq = _fe.freqs()
    for noun in sorted(_freq, key=lambda k: len(_freq[k]), reverse=True):
        print(noun, len(_freq[noun]), ' - ', normalize(_freq[noun][0].sent))
