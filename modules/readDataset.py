import pandas as pd
from reviewMethods import sentence_score_calculator

def constructDataframe(file_path):
    df = pd.read_excel(file_path)
    review_column = df['review_text'].head(10)
    output = []

    for review in review_column:
        scores = sentence_score_calculator(review)
        output.append(scores)

    return output