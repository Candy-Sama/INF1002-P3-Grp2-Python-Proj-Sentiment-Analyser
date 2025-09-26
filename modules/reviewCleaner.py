import contractions
import re

def reviewFormatter(review):
    listOfSentences = []
    listOfCleanedSentences = []
    review = re.sub('_x000D_','',review)

    # Split review into sentences
    for sentence in review.split(r'.'):
        if len(sentence) != 0:
            listOfSentences.append(sentence.strip())

    # Remove parenthesis contractions by splitting them into their base
    for word in listOfSentences:
            word = re.sub(r'\-',' ',word)
            word = re.sub(r'[^a-zA-Z\d\s:]','',word)
            listOfCleanedSentences.append(contractions.fix(word))

    return listOfCleanedSentences