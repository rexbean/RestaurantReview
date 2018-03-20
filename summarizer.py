import json
import re
import operator
import statistics
from collections import namedtuple, defaultdict
import spacy

Noun = namedtuple('Noun', ['lemma', 'chunk'])
Opinion = namedtuple('Opinion', ['subjs', 'chunk', 'negation'])
Summary = namedtuple('Summary', ['lemma', 'positive', 'negative'])


class Summarizer:
    nlp = spacy.load('en_core_web_lg')
    excellent, poor = nlp('excellent poor')
    BAN_WORDS = ['lot', 'something', 'anything', 'everything', 'time']
    # from vader --start
    B_INCR = 0.293
    B_DECR = -0.293
    N_SCALAR = -0.74
    C_INCR = 0.733

    PUNC_LIST = [".", "!", "?", ",", ";", ":", "-", "'", "\"",
                 "!!", "!!!", "??", "???", "?!?", "!?!", "?!?!", "!?!?"]
    NEGATE = {"aint", "arent", "cannot", "cant", "couldnt", "darent", "didnt", "doesnt",
              "ain't", "aren't", "can't", "couldn't", "daren't", "didn't", "doesn't",
              "dont", "hadnt", "hasnt", "havent", "isnt", "mightnt", "mustnt", "neither",
              "don't", "hadn't", "hasn't", "haven't", "isn't", "mightn't", "mustn't",
              "neednt", "needn't", "never", "none", "nope", "nor", "not", "nothing", "nowhere",
              "oughtnt", "shant", "shouldnt", "uhuh", "wasnt", "werent",
              "oughtn't", "shan't", "shouldn't", "uh-uh", "wasn't", "weren't",
              "without", "wont", "wouldnt", "won't", "wouldn't", "rarely", "seldom", "despite"}
    BOOSTER_DICT = \
        {"absolutely": B_INCR, "amazingly": B_INCR, "awfully": B_INCR, "completely": B_INCR, "considerably": B_INCR,
         "decidedly": B_INCR, "deeply": B_INCR, "effing": B_INCR, "enormously": B_INCR,
         "entirely": B_INCR, "especially": B_INCR, "exceptionally": B_INCR, "extremely": B_INCR,
         "fabulously": B_INCR, "flipping": B_INCR, "flippin": B_INCR,
         "fricking": B_INCR, "frickin": B_INCR, "frigging": B_INCR, "friggin": B_INCR, "fully": B_INCR,
         "fucking": B_INCR,
         "greatly": B_INCR, "hella": B_INCR, "highly": B_INCR, "hugely": B_INCR, "incredibly": B_INCR,
         "intensely": B_INCR, "majorly": B_INCR, "more": B_INCR, "most": B_INCR, "particularly": B_INCR,
         "purely": B_INCR, "quite": B_INCR, "really": B_INCR, "remarkably": B_INCR,
         "so": B_INCR, "substantially": B_INCR,
         "thoroughly": B_INCR, "totally": B_INCR, "tremendously": B_INCR,
         "uber": B_INCR, "unbelievably": B_INCR, "unusually": B_INCR, "utterly": B_INCR,
         "very": B_INCR,
         "almost": B_DECR, "barely": B_DECR, "hardly": B_DECR, "just enough": B_DECR,
         "kind of": B_DECR, "kinda": B_DECR, "kindof": B_DECR, "kind-of": B_DECR,
         "less": B_DECR, "little": B_DECR, "marginally": B_DECR, "occasionally": B_DECR, "partly": B_DECR,
         "scarcely": B_DECR, "slightly": B_DECR, "somewhat": B_DECR,
         "sort of": B_DECR, "sorta": B_DECR, "sortof": B_DECR, "sort-of": B_DECR}
    # from vader --end
    print('model loaded.')

    def __init__(self, reviews):
        self.raw = reviews
        self.doc = self.nlp(re.sub('(?<![.!?])\n+', '.\n', reviews))

    def nouns(self):
        """ return [Noun] """
        for chunk in self.doc.noun_chunks:
            lemma = [token.lemma_ for token in chunk
                     # CD=cardinal number, DT=determiner, WP=wh-pronoun(personal)
                     # PRP=pronoun(personal), PRP$=pronoun(possessive)
                     # JJ=adjective, JJR=adjective(comparative), JJS=adjective(superlative)
                     # RB=adverb, RBR=adverb(comparative), RBS=adverb(superlative)
                     if token.tag_ not in ('CD', 'DT', 'WP', 'PRP', 'PRP$', 'JJ', 'JJR', 'JJS', 'RB', 'RBR', 'RBS')
                     # NN=noun(singular or mass), NNS=noun(plural)
                     and (not token.is_stop or token.tag_ in ('NN', 'NNS'))
                     and token.lemma_ not in self.BAN_WORDS
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
    def opinions(freqs):
        """ return {lemma:[Opinion]} """
        opinions = defaultdict(list)
        for lemma, chunks in freqs.items():
            for chunk in chunks:
                # JJ=adjective, JJR=adjective(comparative), JJS=adjective(superlative)
                subjs = [word for word in chunk.root.subtree if word.tag_ in ('JJ', 'JJR', 'JJS')]
                if subjs:
                    opinions[lemma].append(Opinion(subjs, chunk,
                                                   any([token.dep_ == 'neg' for token in chunk.root.subtree])))
                    continue
                subjs = [word for word in chunk.root.head.subtree if word.tag_ in ('JJ', 'JJR', 'JJS')]
                if subjs:
                    opinions[lemma].append(Opinion(subjs, chunk,
                                                   len(list(chunk.root.head.subtree)) < 12 and
                                                   any([token.dep_ == 'neg' for token in chunk.root.head.subtree])))
                    continue
        return opinions

    @classmethod
    def word_sentiments(cls, words):
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

    @classmethod
    def _never_check(cls, sentence, start_i, i):
        if start_i == 0:
            if cls._negated(str(sentence[i - 1])):
                return cls.N_SCALAR
        if start_i == 1:
            if str(sentence[i - 2]) == "never" and (str(sentence[i - 1]) == "so" or str(sentence[i - 1]) == "this"):
                return 1.5
            elif cls._negated(str(sentence[i - 2])):
                return cls.N_SCALAR
        if start_i == 2:
            if str(sentence[i - 3]) == "never" and \
                    (str(sentence[i - 2]) == "so" or str(sentence[i - 2]) == "this") or \
                    (str(sentence[i - 1]) == "so" or str(sentence[i - 1]) == "this"):
                return 1.25
            elif cls._negated(str(sentence[i - 3])):
                return cls.N_SCALAR
        return 1.0

    @classmethod
    def _scalar_booster(cls, word, sentiment):
        """
        Check if the preceding words increase, decrease, or negate/nullify the
        sentiment
        """
        scalar = 0.0
        word_lower = word.lower_
        if word_lower in cls.BOOSTER_DICT:
            scalar = cls.BOOSTER_DICT[word_lower]
            if sentiment < 0:
                scalar *= -1
            # check if booster/dampener word is in ALLCAPS (while others aren't)
            if word.is_upper:
                if sentiment > 0:
                    scalar += cls.C_INCR
                else:
                    scalar -= cls.C_INCR
        return scalar

    @classmethod
    def _negated(cls, word):
        if word.lower() in cls.NEGATE or "n't" in word.lower():
            return True
        return False

    @classmethod
    def sent_sentiments(cls, opinion, sentiments):
        # sentiment = sum([sentiments.get(subj.lemma_, 0) for subj in opinion.subjs])
        # if opinion.negation:
        #     sentiment = -0.8 * sentiment
        sents = []
        for subj in opinion.subjs:
            sentiment = sentiments.get(subj.lemma_, 0)
            # check if the subject word is in ALLCAPS
            if subj.is_upper:
                if sentiment > 0:
                    sentiment += cls.C_INCR
                else:
                    sentiment -= cls.C_INCR

            for start_i in range(0, 3):
                i = subj.i - opinion.chunk.sent.start
                if i > start_i:
                    # Check if the preceding words increase, decrease, or negate/nullify the sentiment
                    s = cls._scalar_booster(opinion.chunk.sent[i - (start_i + 1)], sentiment)
                    if start_i == 1 and s != 0:
                        s = s * 0.95
                    if start_i == 2 and s != 0:
                        s = s * 0.9
                    sentiment = sentiment + s

                    sentiment *= cls._never_check(opinion.chunk.sent, start_i, i)
            sents.append(sentiment)
        return sum(sents)

    # Evaluate the punctuation emphasis to sentences.

    def punctuation_emphasis(self, opinion):
        # add emphasis from exclamation points and question marks
        ep_amplifier = self._amplify_ep(opinion.chunk.sent)
        qm_amplifier = self._amplify_qm(opinion.chunk.sent)
        punct_amplifier = ep_amplifier + qm_amplifier
        return punct_amplifier

    def _amplify_ep(self, text):
        # check for added emphasis resulting from exclamation points (up to 4 of them)
        ep_count = len([token for token in text if str(token) == "!"])
        if ep_count > 4:
            ep_count = 4
        # (empirically derived mean sentiment intensity rating increase for
        # exclamation points)
        ep_amplifier = ep_count * 0.292
        return ep_amplifier

    def _amplify_qm(self, text):
        # check for added emphasis resulting from question marks (2 or 3+)
        qm_count = len([token for token in text if str(token) == "?"])
        qm_amplifier = 0
        if qm_count > 1:
            if qm_count <= 3:
                # (empirically derived mean sentiment intensity rating increase for
                # question marks)
                qm_amplifier = qm_count * 0.18
            else:
                qm_amplifier = 0.96
        return qm_amplifier

    def summary(self):
        """ return sorted [Summary] """
        opinions = self.opinions(self.freqs(self.nouns()))
        sentiments = self.word_sentiments({subj.lemma_: subj for opinions_ in opinions.values()
                                           for opinion in opinions_ for subj in opinion.subjs}.values())
        summary = defaultdict(lambda: [[], [], 0])
        for lemma, opis in opinions.items():
            for opi in opis:
                sentiment = self.sent_sentiments(opi, sentiments)

                # Implement punctuation emphasis in summarization
                punct_emph = self.punctuation_emphasis(opi)
                if sentiment > 0:
                    sentiment += punct_emph
                elif sentiment < 0:
                    sentiment -= punct_emph

                if sentiment > 0:
                    summary[lemma][0].append((opi.chunk, sentiment))
                    summary[lemma][2] += 1
                elif sentiment < 0:
                    summary[lemma][1].append((opi.chunk, sentiment))
                    summary[lemma][2] += 1
        return [Summary(lemma,
                        [chunk[0] for chunk in sorted(summary[lemma][0], key=operator.itemgetter(1), reverse=True)],
                        [chunk[0] for chunk in sorted(summary[lemma][1], key=operator.itemgetter(1), reverse=False)])
                for lemma in sorted(summary, key=lambda k: summary[k][2], reverse=True)]


def norm(raw):
    return re.sub(r'\s+', ' ', str(raw))


if __name__ == "__main__":
    print('parsing text ...')
    with open('review_data/9.json') as file:
        _s = Summarizer('\n\n'.join(item['review'] for item in json.load(file)[:10]))

    for l, c in _s.nouns():
        subjs = [word for word in c.root.subtree if word.tag_ in ('JJ', 'JJR', 'JJS')]
        if subjs:
            negated = any([token.dep_ == 'neg' for token in c.root.subtree])
            print(l, ' - ', negated, subjs, ' - ', norm(c.sent))
            input('press')
            continue
        subjs = [word for word in c.root.head.subtree if word.tag_ in ('JJ', 'JJR', 'JJS')]
        if subjs:
            negated = len(list(c.root.head.subtree)) < 12 and \
                      any([token.dep_ == 'neg' for token in c.root.head.subtree])
            print(l, ' - ', negated, subjs, ' - ', norm(c.sent))
            input('press')
            continue
        print(l, ' - ', 'not detected', ' - ', norm(c.sent))
        input('press')
    # _summary = _s.summary()
    # for i, f in enumerate(_summary):
    #     print(str(i + 1) + '.', '[' + f.lemma + ']', str(len(f.positive)) + '/' + str(len(f.negative)))
    #
    #     print('\tpositive:')
    #     for n in f.positive[:3]:
    #         print('\t', norm(n.sent))
    #
    #     print('\tnegative:')
    #     for n in f.negative[:3]:
    #         print('\t', norm(n.sent))
