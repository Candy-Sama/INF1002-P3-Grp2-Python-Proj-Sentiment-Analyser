import pandas as pd
import reviewMethods as reviewMethods
import re

# Get sentence and score of review (Zacc's Code)
def get_sentence_scores(file_path):
    df = pd.read_excel(file_path)
    review_column = df['review_text'].head(10)
    output = []

    for review in review_column:
        scores = reviewMethods.sentence_score_calculator(review)
        output.append(scores)

    return output
    
# Get raw review to display to users (Zacc's & Mus' Code)
def get_reviews(file_path):
    df = pd.read_excel(file_path)
    outputList = []
    for eachReview in range(len(df['review_text'].head(10))):
        review_text = df['review_text'].iloc[eachReview]
        review_text = re.sub(r'\n', '', review_text)  # Replace newlines
        review_text = re.sub(r'_x000D_', '', review_text)  # Replace '_x000D_'
        review_text = re.sub(r'\s+', ' ', review_text).strip()  # Replace multiple spaces with a single space

        outputList.append({
            "review_id": df['review_id'].iloc[eachReview],
            "review_text": review_text
        })

    return outputList