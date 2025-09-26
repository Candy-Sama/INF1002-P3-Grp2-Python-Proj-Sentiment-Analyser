import os
import pandas as pd
import reviewScorer

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
file_path = os.path.join(BASE_DIR, "..", "steam_reviews_315210.xlsx")

df = pd.read_excel(file_path)

review_column = df['review_text'].head(10)

for review in review_column:
    scores = reviewScorer.sentence_score_calculator(review)
    for i in range(len(scores)):
        output = scores[i]