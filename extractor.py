import json
import re
import math
import random
import statistics
from collections import defaultdict
import spacy


class Extractor:
    nlp = spacy.load('en_core_web_lg')
    positive = nlp(' '.join(
        ['good', 'great', 'nice', 'excellent', 'decent', 'fantastic', 'wonderful', 'awesome', 'perfect',
         'happy', 'amazing', 'enjoyable', 'healthy', 'incredible', 'fabulous', 'fresh', 'delicious', 'exciting',
         'fun', 'excited', 'yummy', 'phenomenal', 'satisfying', 'satisfied', 'cute', 'memorable', 'stellar',
         'crisp', 'popular', 'honorable', 'classic', 'plentiful', 'spectacular', 'delicate', 'artistic', 'cool',
         'presentable', 'heavenly', 'legendary', 'expansive', 'organized', 'kind', 'best', 'glad', 'consistent',
         'easy', 'super', 'superb', 'impressed', 'worth', 'worthy', 'worthwhile', 'clean', 'friendly', 'tasty']))
    negative = nlp(' '.join(
        ['bad', 'fair', 'difficult', 'terrible', 'awful', 'horrible', 'mediocre', 'disappointed',
         'disappointing', 'expensive', 'pricey', 'costly', 'weird', 'boring', 'tired', 'shitty', 'ill', 'silly',
         'worried', 'mad', 'tricky', 'heavy', 'ridiculous', 'dirty', 'lame', 'limited', 'confusing', 'confused',
         'ordinary', 'sloppy', 'annoyed', 'annoying', 'freaking', 'dead', 'overrated', 'average', 'bland',
         'insane', 'disgusting', 'rotten', 'messy', 'scarce', 'unhealthy', 'horrendous', 'crowded', 'obscure',
         'stale', 'irritating', 'daunting', 'stingy', 'gross', 'outrageous', 'mundane', 'allergic', 'chaotic']))
    print('model loaded.')

    def __init__(self, text):
        self.raw = text
        self.doc = self.nlp(text)

    def nouns(self):
        for span in self.doc.noun_chunks:
            # TODO: subject/object filter
            lemma = [token.lemma_ for token in span
                     # CD=cardinal number, DT=determiner, WP=wh-pronoun(personal)
                     # PRP=pronoun(personal), PRP$=pronoun(possessive)
                     if token.tag_ not in ('CD', 'DT', 'WP', 'PRP', 'PRP$')
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
                adj = [word for word in noun.root.subtree if word.tag_ in ('JJ', 'JJR', 'JJS')] or \
                      [word for word in noun.root.head.subtree if word.tag_ in ('JJ', 'JJR', 'JJS')]
                if adj:
                    options[lemma].append((adj, noun))
        return options

    def sentiment(self, words):
        positive = math.log2(statistics.mean(
            [2 ** (30 * token.similarity(word)) for token in self.positive for word in words])) / 30
        negative = math.log2(statistics.mean(
            [2 ** (30 * token.similarity(word)) for token in self.negative for word in words])) / 30
        if positive - negative > 0.15:
            return +1
        if negative - positive > 0.15:
            return -1
        return 0

    def summary(self):
        summary = defaultdict(lambda: ([], []))
        for lemma, options in self.options().items():
            for option in options:
                sentiment = self.sentiment(option[0])
                if sentiment > 0:
                    summary[lemma][0].append(option[1])
                if sentiment < 0:
                    summary[lemma][1].append(option[1])
        return [(lemma, summary[lemma][0], summary[lemma][1]) for lemma in
                sorted(summary, key=lambda k: len(summary[k][0]) + len(summary[k][1]), reverse=True)]


if __name__ == "__main__":
    def norm(raw):
        return re.sub(r'\s+', ' ', str(raw))


    with open('review_data/3.json') as file:
        _txt = '\n\n'.join(item['review'] for item in json.load(file))
    _fe = Extractor(_txt)

    # for lemma, noun in _fe.nouns():
    #     print(lemma, '-', norm(noun), '-', norm(noun.sent))
    #     for word in noun:
    #         print('\t', word.text, ':', word.pos_, word.tag_, word.dep_)

    # _freq = _fe.freqs()
    # for n in sorted(_freq, key=lambda k: len(_freq[k]), reverse=True):
    #     print(n, len(_freq[n]

    # _options = _fe.options()
    # for i, n in enumerate(sorted(_options, key=lambda k: len(_options[k]), reverse=True)):
    #     print(i + 1, n, len(_options[n]), '-', set([adj.lemma_ for opt in _options[n] for adj in opt[0]]))

    # for a in set([adj.lemma_ for opts in _fe.options().values() for opt in opts for adj in opt[0]]):
    #     print(a, _fe.sentiment(_fe.nlp(a)))

    _summary = _fe.summary()
    for i, n in enumerate(_summary):
        print(str(i + 1) + '.', '[' + n[0] + ']', str(len(n[1])) + '/' + str(len(n[2])))

        print('\tpositive:')
        positive = n[1]
        if len(positive) > 3:
            positive = random.sample(positive, 3)
        for noun in positive:
            print('\t', norm(noun.sent))

        print('\tnegative:')
        negative = n[2]
        if len(negative) > 3:
            negative = random.sample(negative, 3)
        for noun in negative:
            print('\t', norm(noun.sent))
