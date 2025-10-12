import itertools
import os
import contractions
import re
import sentiment_dict
import pandas as pd
from wordsegment import load, segment

# =============================================================================
# ACTIVE CODE - Currently used functions
# =============================================================================

# Zacc's code (Used by format_review)
def segment_sentence(sentence):
    # Segmentation
    listOfSegmentedResults = []
    for word in sentence.split():
        word = segment(word)
        segmentResult = ' '.join(word)
        listOfSegmentedResults.append(segmentResult)
    combined_string = ' '.join(listOfSegmentedResults)
    return combined_string

# Prepare review for scoring (Zacc's code, edited by Mus) - Used by sentence_score_calculator and score_paragraphs_SlidingWindow
def format_review(review):
    load()
    finalResult = []
    listOfSentences = []
    listOfCleanedSentences = []
    review = re.sub('_x000D_', '', review)

    # Split review into sentences
    # Edited by Ethel: Use proper sentence splitting with multiple punctuation marks
    sentences = re.split(r'[.!?]+', review)
    for sentence in sentences:
        if len(sentence.strip()) != 0:  # Also strip whitespace
            listOfSentences.append(sentence.strip())
    # Remove parenthesis contractions by splitting them into their base
    for sentence in listOfSentences:
            sentence = re.sub(r'\-', ' ', sentence)
            sentence = re.sub(r'[^a-zA-Z\d\s:]', '', sentence)
            listOfCleanedSentences.append(contractions.fix(sentence))
    
    # Segmentation
    for sentence in listOfCleanedSentences:
        finalResult.append(segment_sentence(sentence))
    return finalResult

# Function to calculate sentiment score of each sentence in a review 
# (Zacc and Ethel's code - Optimized for performance) - Called in main.py
def sentence_score_calculator(review_to_be_scored):
    # Cache the sentiment dictionary to avoid repeated calls
    word_scores = sentiment_dict.wordScores()
    
    cleanedSentence = format_review(review_to_be_scored)
    results = []
    
    # Process sentences more efficiently while maintaining original logic
    for sentence in cleanedSentence:
        score = sum(float(word_scores.get(word, 0)) for word in sentence.split())
        results.append([sentence, score])
    
    # Sort once at the end
    sorted_results = sorted(results, key=lambda x: x[1], reverse=True)
    
    return results, sorted_results

# Mus' code - Called in main.py
def score_paragraphs_SlidingWindow(review, window_size=5, step_size=1):
    """
    Core sliding window function for sentiment analysis of paragraphs.
    Original algorithm by Mus, optimized for performance and bug fixes.
           
    Sliding Window Process:
        1. Split given review into sentences using punctuation
        2. Create overlapping windows of sentences
        3. Calculate sentiment score for each window
    """
    if not review or not review.strip():
        return []
    
    # Cache the sentiment dictionary for performance
    word_scores = sentiment_dict.wordScores()
    cleaned_sentences = format_review(review)
    
    if len(cleaned_sentences) < window_size:
        # If review is shorter than window, analyze as single window
        window_size = len(cleaned_sentences)
    
    scored_paragraphs = []
        
    # 1 Apply sliding window technique to create paragraph windows
    # Loop through possible starting positions for windows
    for i in range(0, len(cleaned_sentences) - window_size + 1, step_size):
        
        # Extract current window of sentences
        window_sentences = cleaned_sentences[i:i + window_size]

        # Join sentences into a single paragraph with proper punctuation
        paragraph_text = '. '.join(window_sentences) + '.'
        
        # (1a) Calculate sentiment score for this paragraph window
        # (1b) Sum sentiment scores for all words in the paragraph
        # Fixed: Only score words in current window, not all sentences
        window_score = 0
        for sentence in window_sentences:  # Only score sentences in this window
            for word in sentence.split():
                window_score += float(word_scores.get(word, 0))

        # (1c) Store data about this paragraph window
        scored_paragraphs.append({
            "paragraph": paragraph_text,              # The actual text
            "raw_score": window_score,               # Total sentiment score
            "window_position": i,                    # Starting sentence position
            "sentences_in_window": len(window_sentences)  # Window size used
        })
        
    scored_paragraphs_sorted = sorted(scored_paragraphs, key=lambda x: x["raw_score"], reverse=True)
    return scored_paragraphs_sorted