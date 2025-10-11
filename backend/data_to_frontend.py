import pandas as pd
import reviewMethods
import re

# =============================================================================
# ACTIVE CODE - Currently used functions
# =============================================================================

# Get raw review to display to users (Zacc's & Mus' Code)
def get_reviews(file_path):
    df = pd.read_excel(file_path)
    review_text_column = df['review_text']
    review_ID_column = df['review_id']
    outputList = []
    
    for eachReview in range(len(df['review_text'].head(10))):
        review_text = review_text_column.iloc[eachReview]
        review_text = re.sub('_x000D_', '', review_text)
        review_text = re.sub('\n', '', review_text)
        review_text = re.sub(r'\s+', ' ', review_text).strip()  # Replace multiple spaces with a single space

        outputList.append({
            "review_id": review_ID_column.iloc[eachReview],
            "review_text": review_text
        })

    return outputList

# =============================================================================
# UNUSED CODE - Preserved for future use and reference
# =============================================================================

# Get sentence and score of review (Zacc's Code)
def get_sentence_scores(file_path):
    df = pd.read_excel(file_path)
    review_column = df['review_text'].head(10)
    output = []

    for review in review_column:
        scores = reviewMethods.sentence_score_calculator(review)
        output.append(scores)

    return output