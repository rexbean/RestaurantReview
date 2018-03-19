# for item all in upper case

    if item.isupper():
        if sentiment > 0:
            sentiment += C_INCR
        else:
            sentiment -= C_INCR

# for preceding words ep: adverbs
    def scalar_booster(word, sentiment):
        """
        Check if the preceding words increase, decrease, or negate/nullify the
        sentiment
        """
        scalar = 0.0
        word_lower = word.lower()
        if word_lower in BOOSTER_DICT:
            scalar = BOOSTER_DICT[word_lower]
            if sentiment < 0:
                scalar *= -1
            #check if booster/dampener word is in ALLCAPS (while others aren't)
            if word.isupper():
                if sentiment > 0:
                    scalar += C_INCR
                else: scalar -= C_INCR
        return scalar
    
## add in for-loop

        s = scalar_booster(words_and_emoticons[i-(start_i+1)], sentiment)
        if start_i == 1 and s != 0:
            s = s*0.95
        if start_i == 2 and s != 0:
            s = s*0.9
        sentiment = sentiment+s


@classmethod
class PunctEmph(object):
    """
    Evaluate the punctuation emphasis to sentences.
    """
    def __init__(self, text):
        # add emphasis from exclamation points and question marks
        ep_amplifier = self._amplify_ep(text)
        qm_amplifier = self._amplify_qm(text)
        self.punct_amplifier = ep_amplifier+qm_amplifier

    def _amplify_ep(self, text):
        # check for added emphasis resulting from exclamation points (up to 4 of them)
        ep_count = text.count("!")
        if ep_count > 4:
            ep_count = 4
        # (empirically derived mean sentiment intensity rating increase for
        # exclamation points)
        ep_amplifier = ep_count*0.292
        return ep_amplifier

    def _amplify_qm(self, text):
        # check for added emphasis resulting from question marks (2 or 3+)
        qm_count = text.count("?")
        qm_amplifier = 0
        if qm_count > 1:
            if qm_count <= 3:
                # (empirically derived mean sentiment intensity rating increase for
                # question marks)
                qm_amplifier = qm_count*0.18
            else:
                qm_amplifier = 0.96
        return qm_amplifier


# Implementation in the sentiment summarization method
    punct_emph = PunctEmph(text)
    if sum_s > 0:
        sum_s += punct_emph.punct_amplifier
    elif  sum_s < 0:
        sum_s -= punct_emph.punct_amplifier