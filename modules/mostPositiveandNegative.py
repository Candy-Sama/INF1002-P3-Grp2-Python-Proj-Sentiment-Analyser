"""
Steam Review Sentiment Analysis with Sliding Window Technique
============================================================

This module analyzes the given to find the most positive and negative 
paragraphs within each individual review using a sliding window approach.

Author: Group 2 - INT1002-P3
Date: September 2025
"""

# Import required modules for the sentiment analysis system
import getSteamReviewsData      # Custom module to fetch Steam review data via API
import reviewMethods           # Custom module to clean and format review text
import sentimentDictionary     # Custom module to load word sentiment scores from CSV
from datetime import datetime  # For timestamping analysis results
import json                   # For saving analysis results to JSON files
import re                     # For regular expressions to split text into sentences

def score_sentences(reviews, sentiment_dict): #Ethel's code
    scored_sentences = []

    # Process each review in the input list
    for review in reviews:
        # Extract review text, provide empty string as fallback
        text = review.get("review", "")
        if not text:   # Skip reviews with no text content
            continue

        # Clean the review text using the custom reviewFormatter
        # Note: reviewFormatter returns a list of cleaned sentences
        cleaned_list = reviewMethods.reviewFormatter(text)
        
        # Convert list of sentences back to single string if needed
        cleaned = ' '.join(cleaned_list) if isinstance(cleaned_list, list) else cleaned_list
        
        # Split cleaned text into individual words for scoring
        words = cleaned.split()
        
        # Calculate total sentiment score by summing scores for each word
        # Uses sentiment_dict.get(word, 0) to return 0 for unknown words
        total_score = sum(sentiment_dict.get(word, 0) for word in words) 

        # Store the sentence data with its calculated score
        scored_sentences.append({
            "sentence": cleaned,           # The cleaned review text
            "normalised_score": total_score # Total sentiment score
        })

    return scored_sentences

def score_paragraphs_SlidingWindow(reviews, sentiment_dict, window_size=5, step_size=1):  #Mus Code
    """
    Core sliding window function for sentiment analysis of paragraphs.
    
    This function implements the sliding window technique to analyze paragraphs 
    within reviews. It creates overlapping windows of sentences and calculates 
    sentiment scores for each window, allowing us to find the most positive 
    and negative content within reviews.
    
    Stuff to take in:
        reviews (list): List of review dictionaries containing review text
        sentiment_dict (dict): Dictionary mapping words to sentiment scores
        window_size (int): Number of sentences per window (default: 5)
        step_size (int): How many sentences to advance the window (default: 1)
    
    Returns:
        list: List of scored paragraph windows, each containing:
            - paragraph: The text of the paragraph (joined sentences)
            - raw_score: Total sentiment score for the paragraph
            - normalised_score: Score divided by word count (normalized)
            - word_count: Number of words in the paragraph
            - review_index: Which review this paragraph came from
            - window_position: Starting position of window in sentence list
            - sentences_in_window: Number of sentences in this window
            
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
        cleaned_sentences = reviewMethods.reviewFormatter(text)
        
        # Filter out empty sentences and ensure we have clean data
        sentences = [s.strip() for s in cleaned_sentences if s.strip()] #Cleaned sentences list by removing empties using strip()
        
        # Apply sliding window technique to create paragraph windows
        # Loop through possible starting positions for windows
        for i in range(0, len(sentences) - window_size + 1, step_size):
            
            # Extract current window of sentences
            window_sentences = sentences[i:i + window_size]
            
            # Join sentences into a single paragraph with proper punctuation
            paragraph_text = '. '.join(window_sentences) + '.'
            
            # Calculate sentiment score for this paragraph window
            # Convert to lowercase for word matching
            words = paragraph_text.lower().split()
            
            # Sum sentiment scores for all words in the paragraph
            # Unknown words get score of 0 via dict.get(word, 0)
            window_score = sum(sentiment_dict.get(word, 0) for word in words)
            
            # Normalize score by word count to handle different paragraph lengths
            # This allows fair comparison between long and short paragraphs
            normalised_score = window_score / len(words) if words else 0
            
            # Store comprehensive data about this paragraph window
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

def get_most_positive_paragraphs(scored_paragraphs, top_n=10): #Mus Code
    # Get the top N most positive paragraphs by sorting in descending order
    sorted_paragraphs = sorted(scored_paragraphs, key=lambda x: x["normalised_score"], reverse=True)
    return sorted_paragraphs[:top_n]

def get_most_negative_paragraphs(scored_paragraphs, top_n=10): #Mus Code
    # Get the top N most negative paragraphs by sorting in ascending order
    sorted_paragraphs = sorted(scored_paragraphs, key=lambda x: x["normalised_score"]) 
    return sorted_paragraphs[:top_n]

def analyse_individual_reviews(reviews, sentiment_dict, window_size=3, step_size=1, max_reviews=10): #Mus Code
    """
    Analyze each review individually to find most positive/negative content within each review.
    This is the core function for individual review analysis, identifying the best and worst
    sentiment content within each review using sliding window technique.
    """
    analysed_reviews = []
    
    # Limit analysis to specified number of reviews for performance
    reviews_to_analyse = reviews[:max_reviews]
    
    # Process each review individually
    for review_idx, review in enumerate(reviews_to_analyse):
        text = review.get("review", "")
        if not text:
            continue  # Skip reviews with no text content
            
        
        # Apply sliding window analysis to this specific review
        review_paragraphs = score_paragraphs_SlidingWindow([review], sentiment_dict, window_size, step_size)
        
        # Score individual sentences within this review
        review_sentences = score_sentences([review], sentiment_dict)
        
        # Skip review if analysis failed
        if not review_paragraphs or not review_sentences:
            continue
            
        # Find the most positive and negative paragraphs within this review
        best_paragraph = max(review_paragraphs, key=lambda x: x["normalised_score"]) if review_paragraphs else None # Find the paragraph with the highest normalised score
        worst_paragraph = min(review_paragraphs, key=lambda x: x["normalised_score"]) if review_paragraphs else None # Find the paragraph with the lowest normalised score
        
        # Handle potential key variations between normalised/normalized spelling
        sentence_key = "normalised_score" if review_sentences and "normalised_score" in review_sentences[0] else "normalized_score" # Fallback for American spelling
        # Find the most positive and negative sentences within this review
        best_sentence = max(review_sentences, key=lambda x: x[sentence_key]) if review_sentences else None # Find the sentence with the highest normalised score 
        worst_sentence = min(review_sentences, key=lambda x: x[sentence_key]) if review_sentences else None # Find the sentence with the lowest normalised score

        # Calculate comprehensive statistics for this review
        paragraph_scores = [p["normalised_score"] for p in review_paragraphs] # List of paragraph scores
        sentence_scores = [s["normalised_score"] for s in review_sentences] # List of sentence scores
        
        # Compute average scores for paragraphs and sentences
        avg_paragraph_score = sum(paragraph_scores) / len(paragraph_scores) if paragraph_scores else 0
        avg_sentence_score = sum(sentence_scores) / len(sentence_scores) if sentence_scores else 0
        
        # Compile comprehensive analysis results for this review
        analysed_review = { #create a dictionary to hold all the analysed data for this review
            "review_index": review_idx,                    # Review position in original list
            "original_review": review,                     # Complete original review data
            "review_text_preview": text[:200] + "..." if len(text) > 200 else text,  # Preview for display
            "statistics": {
                "total_paragraphs": len(review_paragraphs),      # Number of sliding windows created
                "total_sentences": len(review_sentences),        # Number of individual sentences
                "avg_paragraph_score": avg_paragraph_score,      # Average paragraph sentiment
                "avg_sentence_score": avg_sentence_score,        # Average sentence sentiment
                "score_range_paragraphs": max(paragraph_scores) - min(paragraph_scores) if paragraph_scores else 0,  # Sentiment range
                "score_range_sentences": max(sentence_scores) - min(sentence_scores) if sentence_scores else 0      # Sentiment range
            },
            "best_paragraph": best_paragraph,              # Most positive paragraph data
            "worst_paragraph": worst_paragraph,            # Most negative paragraph data
            "best_sentence": best_sentence,                # Most positive sentence data
            "worst_sentence": worst_sentence,              # Most negative sentence data
            "all_paragraphs": review_paragraphs,           # Complete paragraph analysis
            "all_sentences": review_sentences              # Complete sentence analysis
        }
        
        analysed_reviews.append(analysed_review) #append the analysed review to the list
    
    return analysed_reviews # Return all analysed reviews in a list of dictionaries

