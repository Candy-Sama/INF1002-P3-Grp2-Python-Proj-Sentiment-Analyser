import contractions

sampleReview = r"This game is unbelievably amazing if your sole purpose in life is to have a sweaty, fat 12-year-old plow their scythe up your anal cavity and rip out all vital organs. Brawhalla's vast range of unique combos and weapons exhibits such robust creativity to the extent that players only require two brain cells to be godly in this game! Furthermore, Brawhalla’s community is truly the pinnacle of gaming culture, where many players demonstrate good sportsmanship through a variety of fun emojis! And occasionally, players wish to further connect by inviting you to custom lobbies, to enact thoughtful exchanges with one another! I am starting to lose count of the amount of times I have been told to kill myself!! This game’s only made me break two monitors! Only two!! If that’s not considered a steal, then I don’t know what is! Another positive aspect I feel is overlooked is its mysterious attributes. I will never know the degree of skill my opponent is going to have despite the claimed “accuracy” of ELO rating! Hell, I was at 1965 and plummeted back to gold! And I still got paired with Diamond Ranks! This obscure inconsistency adds a whole new excitement as I do not know what the fuck I am going to do to myself after a match! I am very appreciative of the experience Brawhalla has provided me, as it has excavated whole new emotions that I had yet to discover. To summarize, if you’re looking for that extra push to jump off that cliff or bridge, then this is the game for you!"

def reviewFormatter():
    listOfWords = []

    for word in sampleReview.split():
        listOfWords.append(contractions.fix(word))

    formattedReview = ' '.join(listOfWords)

    print(formattedReview)

reviewFormatter()



