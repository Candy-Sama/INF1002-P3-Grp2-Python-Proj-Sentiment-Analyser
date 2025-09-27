"""
Steam Review Sentiment Analysis with Sliding Window Technique
============================================================

This module analyzes the given to find the most positive and negative 
paragraphs within each individual review using a sliding window approach.

Author: Group 2 - INT1002-P3
Date: September 2025
"""

# Import required modules for the sentiment analysis system
import modules.fetch_steam_data as fetch_steam_data      # Custom module to fetch Steam review data via API
import reviewMethods           # Custom module to clean and format review text
import modules.sentiment_dict as sentiment_dict     # Custom module to load word sentiment scores from CSV
from datetime import datetime  # For timestamping analysis results
import json                   # For saving analysis results to JSON files
import re                     # For regular expressions to split text into sentences
import pandas as pd          # For reading the excel file containing reviews

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
        cleaned_list = reviewMethods.format_review(text)
        
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

