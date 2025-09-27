import os
import contractions
import re
import sentiment_dict as sentiment_dict
import pandas as pd

# Prepare review for scoring (Zacc's Code)
def format_review(review):
    listOfSentences = []
    listOfCleanedSentences = []
    review = re.sub('_x000D_', '', review)

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

# Function to calculate sentiment score of each sentence in a review (Zacc's Code)
def sentence_score_calculator(review_to_be_scored):
    sentenceScore = []
    results = []
    cleanedSentence = format_review(review_to_be_scored)

    for sentence in cleanedSentence:
        score = 0
        for word in sentence.split():
            if word in sentiment_dict.wordScores().keys():
                score += float(sentiment_dict.wordScores()[word])
            else:
                pass
        sentenceScore.append(score)

    for i in range(len(cleanedSentence)):
        results.append([cleanedSentence[i],sentenceScore[i]])

    return results

# Code to check the length of reviews
def findReviewLengths(): #Get the PD dataframe of reviews (Mus code)

    #create a list to store the lengths of each review
    review_lengths = []

    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(BASE_DIR, "..", "data", "steam_reviews_315210.xlsx") # Path to the excel file
    df = pd.read_excel(file_path)

    largest_review, smallest_review, largest_review_text, smallest_review_text = 0, 0, "", ""

    for eachReview in df['review_text'].head(10): # Loop through each review in the dataframe
        if (largest_review < len(eachReview.split())): # Check if the current review is larger than the largest review
            largest_review = len(eachReview.split()) # Update the largest review length
            largest_review_text = eachReview # Update the largest review text

        if (smallest_review > len(eachReview.split())) or (smallest_review == 0): # Check if the current review is smaller than the smallest review
            smallest_review = len(eachReview.split()) # Update the smallest review length
            smallest_review_text = eachReview # Update the smallest review text

    review_lengths.append({"length": largest_review, "text": largest_review_text})
    review_lengths.append({"length": smallest_review, "text": smallest_review_text})

    return review_lengths

def score_paragraphs_SlidingWindow(reviews, sentiment_dict, window_size=5, step_size=1):  #Mus Code
    """
    Core sliding window function for sentiment analysis of paragraphs.
           
    Sliding Window Process:
        1. Split each review into sentences using punctuation
        2. Create overlapping windows of sentences
        3. Calculate sentiment score for each window
    """
    scored_paragraphs = []
    
    # Process each review individually
    for review_idx, review in enumerate(reviews):
        # Extract review text with fallback to empty string
        text = review.get("review", "")
        if not text:
            continue
            
        # Clean the review text using reviewCleaner
        cleaned_sentences = format_review(text)
        
        # 1 Apply sliding window technique to create paragraph windows
        # Loop through possible starting positions for windows
        for i in range(0, len(cleaned_sentences) - window_size + 1, step_size):
            
            # Extract current window of sentences
            window_sentences = cleaned_sentences[i:i + window_size]

            # Join sentences into a single paragraph with proper punctuation
            paragraph_text = '. '.join(window_sentences) + '.'
            
            # (1a) Calculate sentiment score for this paragraph window
            # Convert to lowercase for word matching
            words = paragraph_text.lower().split()
            
            # (1b) Sum sentiment scores for all words in the paragraph
            # Unknown words get score of 0 via dict.get(word, 0)
            window_score = sum(sentiment_dict.get(word, 0) for word in words)

            # (1c) Normalize score by word count to handle different paragraph lengths
            # This allows fair comparison between long and short paragraphs
            normalised_score = window_score / len(words) if words else 0

            # (1d) Store data about this paragraph window
            scored_paragraphs.append({
                "paragraph": paragraph_text,              # The actual text
                "raw_score": window_score,               # Total sentiment score
                "normalised_score": normalised_score,    # Score per word
                "word_count": len(words),                # Number of words
                "review_index": review_idx,              # Which review this came from
                "window_position": i,                    # Starting sentence position
                "sentences_in_window": len(window_sentences)  # Window size used
            })
    
    return scored_paragraphs # Return all scored paragraph windows

def analyse_individual_reviews(reviews, sentiment_dict, window_size=3, step_size=1): #Mus Code
    """
    Analyze each review individually to find most positive/negative content within each review.
    """
    analysed_reviews = []
    
    # Process each review individually
    for review_idx in range(len(reviews)):
        text = reviews[review_idx].get("review", "")
        if not text:
            continue  # Skip reviews with no text content
            
        
        # Apply sliding window analysis to this specific review
        review_paragraphs = score_paragraphs_SlidingWindow([reviews[review_idx]], sentiment_dict, window_size, step_size)
        review_sentences = sentence_score_calculator([reviews[review_idx]], sentiment_dict)

        # Skip review if analysis failed
        if not review_paragraphs or not review_sentences:
            continue
            
        # Find the most positive and negative paragraphs within this review
        best_paragraph = max(review_paragraphs, key=lambda x: x["normalised_score"]) if review_paragraphs else None # Find the paragraph with the highest normalised score
        worst_paragraph = min(review_paragraphs, key=lambda x: x["normalised_score"]) if review_paragraphs else None # Find the paragraph with the lowest normalised score

        # Calculate comprehensive statistics for this review
        paragraph_scores = [p["normalised_score"] for p in review_paragraphs] # List of paragraph scores
        sentence_scores = [s["normalised_score"] for s in review_sentences] # List of sentence scores
        

        analysed_review = {
            "review_index": review_idx,                    # Review position in original list
            "original_review": reviews[review_idx],                     # Complete original review data
            "review_text_preview": text[:200] + "..." if len(text) > 200 else text,  # Preview for display
            "statistics": {
                "total_paragraphs": len(review_paragraphs),      # Number of sliding windows created
                "total_sentences": len(review_sentences),        # Number of individual sentences
                "score_range_paragraphs": max(paragraph_scores) - min(paragraph_scores) if paragraph_scores else 0,  # Sentiment range
                "score_range_sentences": max(sentence_scores) - min(sentence_scores) if sentence_scores else 0      # Sentiment range
            },
            "best_paragraph": best_paragraph,              # Most positive paragraph data
            "worst_paragraph": worst_paragraph,            # Most negative paragraph data
            "all_paragraphs": review_paragraphs,           # Complete paragraph analysis
            "all_sentences": review_sentences              # Complete sentence analysis
        }
        
        analysed_reviews.append(analysed_review)
    
    return analysed_reviews # Return all analysed reviews in a list of dictionaries