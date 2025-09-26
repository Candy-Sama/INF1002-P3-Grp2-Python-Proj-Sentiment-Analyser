import reviewCleaner
import sentimentDictionary

def sentence_score_calculator(review_to_be_scored):
    sentenceScore = []
    results = []
    cleanedSentence = reviewCleaner.reviewFormatter(review_to_be_scored)

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