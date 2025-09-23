import contractions
import re

def reviewFormatter(review):
    listOfWords = []

    # Remove parenthesis contractions by splitting them into their base
    for word in review.split():
        word = re.sub(r'\-',' ',word)
        word = re.sub(r'[^a-zA-Z\d\s:]','',word)
        listOfWords.append(contractions.fix(word))

    formattedReview = ' '.join(listOfWords)

    return formattedReview