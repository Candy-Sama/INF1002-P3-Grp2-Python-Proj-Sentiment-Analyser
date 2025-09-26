import contractions
import re
import sentimentDictionary
import pandas as pd

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


# Function to calculate sentiment score of each sentence in a review
def sentence_score_calculator(review_to_be_scored):
    sentenceScore = []
    results = []
    cleanedSentence = reviewFormatter(review_to_be_scored)

    for sentence in cleanedSentence:
        score = 0
        for word in sentence.split():
            if word in sentimentDictionary.wordScores().keys():
                score += float(sentimentDictionary.wordScores()[word])
            else:
                pass
        sentenceScore.append(score)

    for i in range(len(cleanedSentence)):
        results.append([cleanedSentence[i],sentenceScore[i]])

    return results

# Code to check the length of reviews
def findReviewLengths(reviews): #Get the PD dataframe of reviews

    #create a list to store the lengths of each review
    review_lengths = []

    for eachReview in reviews['review_text']:
        review_lengths.append(len(eachReview.split())) # Get lengths of each review via word count
    review_lengths.sort() # Sort the lengths in ascending order

    # Get the longest and shortest review lengths
    longest_review = review_lengths[-1] if review_lengths else 0 # Handle empty list case
    shortest_review = review_lengths[0] if review_lengths else 0 # Handle empty list case

    return longest_review, shortest_review

