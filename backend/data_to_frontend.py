import pandas as pd
import reviewMethods
import re

# =============================================================================
# ACTIVE CODE - Currently used functions
# =============================================================================

currentDataframe = None

# Get raw review to display to users (Zacc's & Mus' Code) - Called in main.py
def get_all_reviews(file_path):
    df = pd.read_excel(file_path)
    global currentDataframe 
    currentDataframe = df.sample(10) # Random 10 reviews
    review_text_column = currentDataframe['review_text']
    review_ID_column = currentDataframe['review_id']
    outputList = []
    
    for eachReview in range(len(currentDataframe)):
        review_text = review_text_column.iloc[eachReview]
        review_text = re.sub('_x000D_', '', review_text)
        review_text = re.sub('\n', '', review_text)
        review_text = re.sub(r'\s+', ' ', review_text).strip() # Replace multiple spaces with a single space

        outputList.append({
            "review_id": review_ID_column.iloc[eachReview],
            "review_text": review_text
        })

    return outputList

# Zacc's Code - Called in main.py
def get_reviews():
    review_text_column = currentDataframe['review_text']
    review_ID_column = currentDataframe['review_id']
    output_list = []

    for eachReview in range(len(review_text_column)):
        review_text = review_text_column.iloc[eachReview]
        review_text = re.sub('_x000D_', '', review_text)
        review_text = re.sub('\n', '', review_text)
        review_text = re.sub(r'\s+', ' ', review_text).strip() # Replace multiple spaces with a single space

        output_list.append({
            "review_id": review_ID_column.iloc[eachReview],
            "review_text": review_text
        })
    
    return output_list

# =============================================================================
# UNUSED CODE - Preserved for future use and reference
# =============================================================================

# Get sentence and score of review (Zacc's Code) - Not called anywhere
def get_sentence_scores(file_path):
    df = pd.read_excel(file_path)
    review_column = df['review_text'].head(10)
    output = []

    for review in review_column:
        scores = reviewMethods.sentence_score_calculator(review)
        output.append(scores)

    return output