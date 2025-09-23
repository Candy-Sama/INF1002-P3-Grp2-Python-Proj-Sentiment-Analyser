import reviewCleaner
import sentimentDictionary

test_string = r"This game is unbelievably amazing if your sole purpose in life is to have a sweaty, fat 12-year-old plow their scythe up your anal cavity and rip out all vital organs. Brawhalla's vast range of unique combos and weapons exhibits such robust creativity to the extent that players only require two brain cells to be godly in this game! Furthermore, Brawhalla’s community is truly the pinnacle of gaming culture, where many players demonstrate good sportsmanship through a variety of fun emojis! And occasionally, players wish to further connect by inviting you to custom lobbies, to enact thoughtful exchanges with one another! I am starting to lose count of the amount of times I have been told to kill myself!! This game’s only made me break two monitors! Only two!! If that’s not considered a steal, then I don’t know what is! Another positive aspect I feel is overlooked is its mysterious attributes. I will never know the degree of skill my opponent is going to have despite the claimed “accuracy” of ELO rating! Hell, I was at 1965 and plummeted back to gold! And I still got paired with Diamond Ranks! This obscure inconsistency adds a whole new excitement as I do not know what the fuck I am going to do to myself after a match! I am very appreciative of the experience Brawhalla has provided me, as it has excavated whole new emotions that I had yet to discover. To summarize, if you’re looking for that extra push to jump off that cliff or bridge, then this is the game for you!"
test_string2 = r"I've been playing this game for a very long time and maybe have put to many hours into this game but getting older I still find myself coming back to this game here and there. I think this game is great and you get a friend on with you and you can just battle each other till you both hate each other or play duo ranked until you both hate each other but its till great fun."

def sentence_score_calculator(review_to_be_scored):
    score = 0
    sentenceScore = []
    cleanedSentence = reviewCleaner.reviewFormatter(review_to_be_scored)

    for sentence in cleanedSentence:
        for word in sentence.split():
            if word in sentimentDictionary.wordScores().keys():
                score += float(sentimentDictionary.wordScores()[word])
            else:
                pass
        sentenceScore.append(score)

    for i in range(len(cleanedSentence)):
        print(f'{cleanedSentence[i]}: {sentenceScore[i]}\n')

sentence_score_calculator(test_string)