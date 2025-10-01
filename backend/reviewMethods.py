import itertools
import os
import contractions
import re
import sentiment_dict
import pandas as pd
from wordsegment import load, segment

# Prepare review for scoring (Zacc's Code, edited by mus hehe)
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

def segment_sentence(sentence): #Mus code
    # Segmentation
    listOfSegmentedResults = []
    for word in sentence.split():
        word = segment(word)
        segmentResult = ' '.join(word)
        listOfSegmentedResults.append(segmentResult)
    combined_string = ' '.join(listOfSegmentedResults)
    return combined_string

def permutations_of_sentences(review): #Mus Code
    combinatorics = itertools.product([True, False], repeat=len(review) - 1)

    solution = []
    for combination in combinatorics:
        i = 0
        one_such_combination = [review[i]]
        for slab in combination:
            i += 1
            if not slab: # there is a join
                one_such_combination[-1] += review[i]
            else:
                one_such_combination += [review[i]]
        solution.append(one_such_combination)
    return solution

# Function to calculate sentiment score of each sentence in a review 
# (Zacc and Ethel's Code - Optimized for performance)
def sentence_score_calculator(review_to_be_scored):
    """
    Calculate sentiment score for each sentence in a review.
    
    Original algorithm by Zacc and Ethel, optimized for performance:
    - Cache word scores to avoid repeated dictionary lookups
    - Reduce function calls and object creation
    - More efficient list building
    """
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

# ORIGINAL VERSION - Kept for reference and fallback
def sentence_score_calculator_original(review_to_be_scored):
    """
    Original implementation by Zacc and Ethel - kept as backup
    """
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

    sorted_results = sorted(results, key=lambda x: x[1], reverse=True)

    return results, sorted_results

# Code to check the length of reviews
def findReviewLengths(): #Get the PD dataframe of reviews (Mus code)

    #create a list to store the lengths of each review
    review_lengths = []

    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(BASE_DIR, "..", "data", "steam_reviews_315210.xlsx") # Path to the excel file
    
    # Edited by Ethel: Added error handling for file operations
    try:
        df = pd.read_excel(file_path)
    except FileNotFoundError:
        print(f"Error: Could not find file at {file_path}")
        return []
    except Exception as e:
        print(f"Error reading Excel file: {e}")
        return []

    largest_review, smallest_review, largest_review_text, smallest_review_text = 0, 0, "", ""

    # Add error handling for missing columns
    if 'review_text' not in df.columns:
        print("Error: 'review_text' column not found in the DataFrame")
        return []

    for eachReview in df['review_text'].dropna().head(10): # Loop through each review, skip NaN values
        # Convert to string to handle any non-string data types
        eachReview = str(eachReview)
        review_word_count = len(eachReview.split())
        
        if (largest_review < review_word_count): # Check if the current review is larger than the largest review
            largest_review = review_word_count # Update the largest review length
            largest_review_text = eachReview # Update the largest review text

        if (smallest_review > review_word_count) or (smallest_review == 0): # Check if the current review is smaller than the smallest review
            smallest_review = review_word_count # Update the smallest review length
            smallest_review_text = eachReview # Update the smallest review text

    review_lengths.append({"length": largest_review, "text": largest_review_text})
    review_lengths.append({"length": smallest_review, "text": smallest_review_text})

    return review_lengths

def score_paragraphs_SlidingWindow(review, window_size=5, step_size=1):  #Mus Code
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

# ORIGINAL VERSION - Kept for reference and fallback
def score_paragraphs_SlidingWindow_original(review, window_size=5, step_size=1):  #Mus Code
    """
    Original implementation by Mus - kept as backup
    Note: Contains scoring bug where all sentences were scored for each window
    """
    scored_paragraphs = []
    cleaned_sentences = format_review(review)
    window_score = 0
        
    # 1 Apply sliding window technique to create paragraph windows
    # Loop through possible starting positions for windows
    for i in range(0, len(cleaned_sentences) - window_size + 1, step_size):
        
        # Extract current window of sentences
        window_sentences = cleaned_sentences[i:i + window_size]

        # Join sentences into a single paragraph with proper punctuation
        paragraph_text = '. '.join(window_sentences) + '.'
        
        # (1a) Calculate sentiment score for this paragraph window
        # (1b) Sum sentiment scores for all words in the paragraph
        for sentence in cleaned_sentences:  # BUG: This scored ALL sentences, not just window
            score = 0
            for word in sentence.split():
                if word in sentiment_dict.wordScores().keys():
                    score += float(sentiment_dict.wordScores()[word])
                else:
                    pass
            window_score += score

        # (1c) Store data about this paragraph window
        scored_paragraphs.append({
            "paragraph": paragraph_text,              # The actual text
            "raw_score": window_score,               # Total sentiment score
            "window_position": i,                    # Starting sentence position
            "sentences_in_window": len(window_sentences)  # Window size used
        })
    scored_paragraphs_sorted = sorted(scored_paragraphs, key=lambda x: x["raw_score"], reverse=True)
    return scored_paragraphs_sorted


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
        #Ethel Edited: Pass the correct parameters to sentence_score_calculator
        review_sentences = sentence_score_calculator(text)  # Pass the text directly

        # Skip review if analysis failed
        if not review_paragraphs or not review_sentences:
            continue
            
        # Find the most positive and negative paragraphs within this review
        best_paragraph = max(review_paragraphs, key=lambda x: x["normalised_score"]) if review_paragraphs else None # Find the paragraph with the highest normalised score
        worst_paragraph = min(review_paragraphs, key=lambda x: x["normalised_score"]) if review_paragraphs else None # Find the paragraph with the lowest normalised score

        # Calculate comprehensive statistics for this review
        paragraph_scores = [p["normalised_score"] for p in review_paragraphs] # List of paragraph scores
        #Ethel Edited: review_sentences returns [sentence, score] pairs, extract scores correctly
        sentence_scores = [s[1] for s in review_sentences] # List of sentence scores (extract score from [sentence, score] pairs)
        

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