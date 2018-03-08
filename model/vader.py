from nltk.sentiment.vader import SentimentIntensityAnalyzer
from nltk import tokenize


sentences = ["VADER is smart, handsome, and funny.",
             "I just finished my 'paul reubens' and am basking in the glory of the fantastic meats, slaw, and especially bread.",
             "I am not good."
            ]

sid = SentimentIntensityAnalyzer()
for sentence in sentences:
    print(sentence)
    ss = sid.polarity_scores(sentence)
    for k in sorted(ss):
        print('{0}: {1}, '.format(k, ss[k]), end='')
    print()

# paragraph = "Thank you for having the best sandwiches in the South Bay.  I just finished my 'paul reubens' and am basking in the glory of the fantastic meats, slaw, and especially bread. Thank you to all your staff for consistently putting out fine food despite daunting orders."

# lines_list = tokenize.sent_tokenize(paragraph)

# for sentence in lines_list:
#     print(sentence)
#     ss = sid.polarity_scores(sentence)
#     for k in sorted(ss):
#         print('{0}: {1}, '.format(k, ss[k]), end='')
#     print()
