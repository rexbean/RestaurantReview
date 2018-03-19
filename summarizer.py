import json
import re
import operator
import statistics
from collections import namedtuple, defaultdict
import spacy

Noun = namedtuple('Noun', ['lemma', 'chunk'])
Option = namedtuple('Option', ['subjs', 'chunk', 'negation'])
Summary = namedtuple('Summary', ['lemma', 'positive', 'negative'])


class Summarizer:
    nlp = spacy.load('en_core_web_lg')
    excellent, poor = nlp('excellent poor')
    print('model loaded.')

    def __init__(self, reviews):
        self.raw = reviews
        self.doc = self.nlp(reviews)

    def nouns(self):
        """ return [Noun] """
        for chunk in self.doc.noun_chunks:
            lemma = [token.lemma_ for token in chunk
                     # CD=cardinal number, DT=determiner, WP=wh-pronoun(personal)
                     # PRP=pronoun(personal), PRP$=pronoun(possessive)
                     if token.tag_ not in ('CD', 'DT', 'WP', 'PRP', 'PRP$')
                     # NN=noun(singular or mass), NNS=noun(plural)
                     and (not token.is_stop or token.tag_ in ('NN', 'NNS'))
                     and not token.is_punct and not token.is_space]
            if lemma:
                yield Noun(' '.join(lemma), chunk)

    def freqs(self, nouns):
        """ return {lemma:[chunk]} """
        freqs = defaultdict(list)
        for noun in nouns:
            freqs[noun.lemma].append(noun.chunk)
        # define an itemset as frequent if it appears in more than 1% of the review sentences
        threshold = max(3, int(len(list(self.doc.sents)) * 0.01))
        return {lemma: freqs[lemma] for lemma in freqs if len(freqs[lemma]) >= threshold}

    @staticmethod
    def options(freqs):
        """ return {lemma:[Option]} """
        options = defaultdict(list)
        for lemma, chunks in freqs.items():
            for chunk in chunks:
                # JJ=adjective, JJR=adjective(comparative), JJS=adjective(superlative)
                subjs = [word for word in chunk.root.subtree if word.tag_ in ('JJ', 'JJR', 'JJS')]
                if subjs:
                    options[lemma].append(Option(subjs, chunk,
                                                 any([token.dep_ == 'neg' for token in chunk.root.subtree])))
                elif len(list(chunk.root.head.subtree)) < 8:
                    subjs = [word for word in chunk.root.head.subtree if word.tag_ in ('JJ', 'JJR', 'JJS')]
                    if subjs:
                        options[lemma].append(Option(subjs, chunk,
                                                     any([token.dep_ == 'neg' for token in chunk.root.head.subtree])))
        return options

    @classmethod
    def sentiments(cls, words):
        """ return {lemma:float} """
        sentiments = {}
        pos_words, neg_words = [cls.excellent], [cls.poor]
        while True:
            next_pos_words, next_neg_words, next_words = [], [], []
            for word in words:
                pos = [pos_word.similarity(word) for pos_word in pos_words]
                pos = (statistics.median(pos) * 2 + max(pos) * 8) / 10
                neg = [neg_word.similarity(word) for neg_word in neg_words]
                neg = (statistics.median(neg) * 2 + max(neg) * 8) / 10
                if pos > 0.6 and pos - neg > 0.15:
                    next_pos_words.append(word)
                    sentiments[word.lemma_] = pos - neg
                elif neg > 0.6 and neg - pos > 0.15:
                    next_neg_words.append(word)
                    sentiments[word.lemma_] = pos - neg
                else:
                    next_words.append(word)
            if len(next_pos_words) == 0 and len(next_neg_words) == 0:
                break
            # print('---', [word for word in words if word not in next_words])
            pos_words += next_pos_words
            neg_words += next_neg_words
            words = next_words
        # print(len(words), '-', words)
        return sentiments

    def summary(self):
        """ return sorted [Summary] """
        options = self.options(self.freqs(self.nouns()))
        sentiments = self.sentiments({subj.lemma_: subj for options_ in options.values()
                                      for option in options_ for subj in option.subjs}.values())
        summary = defaultdict(lambda: [[], [], 0])
        for lemma, options in options.items():
            for option in options:
                sentiment = sum([sentiments.get(subj.lemma_, 0) for subj in option.subjs])
                if option.negation:
                    sentiment = -0.8 * sentiment
                if sentiment > 0:
                    summary[lemma][0].append((option.chunk, sentiment))
                    summary[lemma][2] += 1
                elif sentiment < 0:
                    summary[lemma][1].append((option.chunk, sentiment))
                    summary[lemma][2] += 1
        return [Summary(lemma,
                        [chunk[0] for chunk in sorted(summary[lemma][0], key=operator.itemgetter(1), reverse=True)],
                        [chunk[0] for chunk in sorted(summary[lemma][1], key=operator.itemgetter(1), reverse=False)])
                for lemma in sorted(summary, key=lambda k: summary[k][2], reverse=True)]


def norm(raw):
    return re.sub(r'\s+', ' ', str(raw))


if __name__ == "__main__":
    print('parsing text ...')
    with open('review_data/3.json') as file:
        _s = Summarizer('\n\n'.join(item['review'] for item in json.load(file)))

    _summary = _s.summary()
    for i, f in enumerate(_summary):
        print(str(i + 1) + '.', '[' + f.lemma + ']', str(len(f.positive)) + '/' + str(len(f.negative)))

        print('\tpositive:')
        for n in f.positive[:3]:
            print('\t', norm(n.sent))

        print('\tnegative:')
        for n in f.negative[:3]:
            print('\t', norm(n.sent))
