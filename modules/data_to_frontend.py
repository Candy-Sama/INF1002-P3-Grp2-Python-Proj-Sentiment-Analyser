import pandas as pd
import reviewMethods
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
    
# Get raw review to display to users (Zacc's Code)
def get_reviews(file_path):
    df = pd.read_excel(file_path)
    review_column = df['review_text'].head(10)
    output = []

    for review in review_column:
        review = re.sub('_x000D_', '', review)
        output.append(review)

    return output

# Get review_id (Zacc's Code)
def get_review_id(file_path):
    df = pd.read_excel(file_path)
    reviewId_column = df['review_id'].head(10)
    output = []

    for review_id in reviewId_column:
        output.append(review_id)

    return output