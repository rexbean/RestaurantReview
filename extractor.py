import json
import re
from collections import defaultdict
import spacy


class Extractor:
    nlp = spacy.load('en')  # en_core_web_lg

    def __init__(self, text):
        self.raw = text
        self.doc = self.nlp(text)

    def nouns(self):
        for span in self.doc.noun_chunks:
            # TODO: subject/object filter
            lemma = [token.lemma_ for token in span
                     # CD=cardinal number, DT=determiner, PRP=pronoun(personal), PRP$=pronoun(possessive)
                     if token.tag_ not in ('CD', 'DT', 'PRP', 'PRP$')
                     # NN=noun(singular or mass), NNS=noun(plural)
                     and (not token.is_stop or token.tag_ in ('NN', 'NNS'))
                     and not token.is_punct]
            if lemma:
                yield ' '.join(lemma), span

    def freqs(self):
        freqs = defaultdict(list)
        for lemma, noun in self.nouns():
            freqs[lemma].append(noun)
        # TODO: fuzzy matching
        # define an itemset as frequent if it appears in more than 1% of the review sentences
        threshold = max(3, int(len(list(self.doc.sents)) * 0.01))
        return {lemma: freqs[lemma] for lemma in freqs if len(freqs[lemma]) >= threshold}

    def options(self):
        options = defaultdict(list)
        for lemma, nouns in self.freqs().items():
            for noun in nouns:
                # JJ=adjective, JJR=adjective(comparative), JJS=adjective(superlative)
                adj = [word.lemma_ for word in noun.root.subtree if word.tag_ in ('JJ', 'JJR', 'JJS')] or \
                      [word.lemma_ for word in noun.root.head.subtree if word.tag_ in ('JJ', 'JJR', 'JJS')]
                if adj:
                    options[lemma].append((adj, noun))
        return options


if __name__ == "__main__":
    def norm(raw):
        return re.sub(r'\s+', ' ', str(raw))


    with open('reviewSpider/reviewSpider/data/IkesLoveandSandwiches.json') as file:
        _txt = '\n\n'.join(item['review'] for item in json.load(file))
    _fe = Extractor(_txt)

    # for lemma, noun in _fe.nouns():
    #     print(lemma, '-', norm(noun), '-', norm(noun.sent))
    #     for word in noun:
    #         print('\t', word.text, ':', word.pos_, word.tag_, word.dep_)

    # _freq = _fe.freqs()
    # for n in sorted(_freq, key=lambda k: len(_freq[k]), reverse=True):
    #     print(n, len(_freq[n]

    _options = _fe.options()
    for i, n in enumerate(sorted(_options, key=lambda k: len(_options[k]), reverse=True)):
        print(i + 1, n, len(_options[n]), '-', set([adj for opt in _options[n] for adj in opt[0]]))
