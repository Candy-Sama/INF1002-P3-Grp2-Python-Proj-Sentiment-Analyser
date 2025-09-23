"""
Steam Review Sentiment Analysis with Sliding Window Technique
============================================================

This module analyzes Steam game reviews to find the most positive and negative 
paragraphs within each individual review using a sliding window approach.

Key Features:
- Fetches Steam reviews for a specific game (app_id)
- Uses sliding window technique to analyze paragraph-level sentiment
- Finds best/worst content within each individual review
- Interactive menu system for detailed review exploration
- Exports results to JSON for further analysis

Author: Group 2 - INT1002-P3
Date: September 2025
"""

# Import required modules for the sentiment analysis system
import getSteamReviewsData      # Custom module to fetch Steam review data via API
import reviewCleaner           # Custom module to clean and format review text
import sentimentDictionary     # Custom module to load word sentiment scores from CSV
from datetime import datetime  # For timestamping analysis results
import json                   # For saving analysis results to JSON files
import re                     # For regular expressions to split text into sentences

def score_sentences(reviews, sentiment_dict):
    """
    Calculate sentiment scores for entire reviews (treated as single sentences).
    
    This function processes a list of reviews and calculates their overall 
    sentiment scores by summing up the sentiment values of all words.
    
    Args:
        reviews (list): List of review dictionaries, each containing a 'review' key
        sentiment_dict (dict): Dictionary mapping words to their sentiment scores
        
    Returns:
        list: List of dictionaries containing:
            - sentence: The cleaned review text
            - normalised_score: Total sentiment score for the review
            
    Process:
        1. Extract review text from each review dictionary
        2. Clean the text using reviewCleaner.reviewFormatter()
        3. Split into individual words
        4. Sum sentiment scores for all words
        5. Return scored sentence data
    """
    scored_sentences = []

    # Process each review in the input list
    for review in reviews:
        # Extract review text, provide empty string as fallback
        text = review.get("review", "")
        if not text:   # Skip reviews with no text content
            continue

        # Clean the review text using the custom reviewFormatter
        # Note: reviewFormatter returns a list of cleaned sentences
        cleaned_list = reviewCleaner.reviewFormatter(text)
        
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

def score_paragraphs(reviews, sentiment_dict, window_size=5, step_size=1): 
    """
    Core sliding window function for sentiment analysis of paragraphs.
    
    This function implements the sliding window technique to analyze paragraphs 
    within reviews. It creates overlapping windows of sentences and calculates 
    sentiment scores for each window, allowing us to find the most positive 
    and negative content within reviews.
    
    Args:
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
        4. Normalize score by word count for fair comparison
        5. Store detailed metadata for each paragraph window
    """
    scored_paragraphs = []
    
    # Process each review individually
    for review_idx, review in enumerate(reviews):
        # Extract review text with fallback to empty string
        text = review.get("review", "")
        if not text:
            continue
            
        # Clean the review text using custom formatter
        # reviewFormatter returns a list of cleaned sentences
        cleaned_sentences = reviewCleaner.reviewFormatter(text)
        
        # Filter out empty sentences and ensure we have clean data
        sentences = [s.strip() for s in cleaned_sentences if s.strip()]
        
        # Apply sliding window technique to create paragraph windows
        # Loop through possible starting positions for windows
        for i in range(0, len(sentences) - window_size + 1, step_size):
            
            # Extract current window of sentences
            # This creates a slice from position i to i+window_size
            window_sentences = sentences[i:i + window_size]
            
            # Join sentences into a single paragraph with proper punctuation
            paragraph_text = '. '.join(window_sentences) + '.'
            
            # Calculate sentiment score for this paragraph window
            # Convert to lowercase for consistent word matching
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
    
    return scored_paragraphs

def get_most_positive_paragraph(scored_paragraphs):
    """
    Find the single most positive paragraph from scored results.
    
    Args:
        scored_paragraphs (list): List of dictionaries containing paragraph scores
                                 from score_paragraphs() function
    
    Returns:
        dict: The paragraph with the highest normalised sentiment score
              Contains keys: text, score, normalised_score, window_position, sentences_in_window
    
    Process:
        - Sorts all paragraphs by normalised_score in descending order
        - Returns the top-ranking (most positive) paragraph
    """
    # Sort by normalised score in descending order (highest score first)
    sorted_paragraphs = sorted(scored_paragraphs, key=lambda x: x["normalised_score"], reverse=True)
    return sorted_paragraphs[0]

def get_most_negative_paragraph(scored_paragraphs):
    """
    Find the single most negative paragraph from scored results.
    
    Args:
        scored_paragraphs (list): List of dictionaries containing paragraph scores
                                 from score_paragraphs() function
    
    Returns:
        dict: The paragraph with the lowest normalised sentiment score
              Contains keys: text, score, normalised_score, window_position, sentences_in_window
    
    Process:
        - Sorts all paragraphs by normalised_score in ascending order
        - Returns the bottom-ranking (most negative) paragraph
    """
    # Sort by normalised score in ascending order (lowest score first)
    sorted_paragraphs = sorted(scored_paragraphs, key=lambda x: x["normalised_score"])
    return sorted_paragraphs[0]

def get_most_positive_paragraphs(scored_paragraphs, top_n=10):
    """
    Get the top N most positive paragraphs from scored results.
    
    Args:
        scored_paragraphs (list): List of dictionaries containing paragraph scores
        top_n (int): Number of top positive paragraphs to return (default: 10)
    
    Returns:
        list: Top N paragraphs sorted by highest normalised scores
              Each paragraph contains: text, score, normalised_score, window_position, sentences_in_window
    
    Process:
        - Sorts all paragraphs by normalised_score in descending order
        - Returns the first top_n paragraphs (most positive)
    """
    # Get the top N most positive paragraphs by sorting in descending order
    sorted_paragraphs = sorted(scored_paragraphs, key=lambda x: x["normalised_score"], reverse=True)
    return sorted_paragraphs[:top_n]

def get_most_negative_paragraphs(scored_paragraphs, top_n=10):
    """
    Get the top N most negative paragraphs from scored results.
    
    Args:
        scored_paragraphs (list): List of dictionaries containing paragraph scores
        top_n (int): Number of top negative paragraphs to return (default: 10)
    
    Returns:
        list: Top N paragraphs sorted by lowest normalised scores
              Each paragraph contains: text, score, normalised_score, window_position, sentences_in_window
    
    Process:
        - Sorts all paragraphs by normalised_score in ascending order
        - Returns the first top_n paragraphs (most negative)
    """
    # Get the top N most negative paragraphs by sorting in ascending order
    sorted_paragraphs = sorted(scored_paragraphs, key=lambda x: x["normalised_score"])
    return sorted_paragraphs[:top_n]

def analyze_individual_reviews(reviews, sentiment_dict, window_size=3, step_size=1, max_reviews=10):
    """
    Analyze each review individually to find most positive/negative content within each review.
    This is the core function for individual review analysis, identifying the best and worst
    sentiment content within each review using sliding window technique.
    
    Args:
        reviews (list): List of review dictionaries containing 'review' text field
        sentiment_dict (dict): Dictionary mapping words to sentiment scores
        window_size (int): Number of sentences per sliding window (default: 3)
        step_size (int): How many sentences to move window each step (default: 1)
        max_reviews (int): Maximum number of reviews to analyze (default: 10)
        
    Returns:
        list: List of analyzed review dictionaries, each containing:
              - Original review data
              - best_paragraph: Most positive paragraph data
              - worst_paragraph: Most negative paragraph data  
              - best_sentence: Most positive sentence data
              - worst_sentence: Most negative sentence data
              - total_paragraphs: Number of paragraphs analyzed
              - total_sentences: Number of sentences analyzed
    
    Process:
        1. Iterates through each review up to max_reviews limit
        2. Applies sliding window analysis to each review individually
        3. Scores both paragraphs (windows) and individual sentences
        4. Identifies best/worst content within each review
        5. Compiles comprehensive analysis results for each review
    """
    analyzed_reviews = []
    
    # Limit analysis to specified number of reviews for performance
    reviews_to_analyze = reviews[:max_reviews]
    
    # Process each review individually
    for review_idx, review in enumerate(reviews_to_analyze):
        text = review.get("review", "")
        if not text:
            continue  # Skip reviews with no text content
            
        print(f"📖 Analyzing review {review_idx + 1}/{len(reviews_to_analyze)}...")
        
        # Apply sliding window analysis to this specific review
        review_paragraphs = score_paragraphs([review], sentiment_dict, window_size, step_size)
        
        # Score individual sentences within this review
        review_sentences = score_sentences([review], sentiment_dict)
        
        # Debug: check what keys are available for troubleshooting
        if review_sentences:
            print(f"Debug: sentence keys: {list(review_sentences[0].keys())}")
        
        # Skip review if analysis failed
        if not review_paragraphs or not review_sentences:
            continue
            
        # Find the most positive and negative paragraphs within this review
        best_paragraph = max(review_paragraphs, key=lambda x: x["normalised_score"]) if review_paragraphs else None
        worst_paragraph = min(review_paragraphs, key=lambda x: x["normalised_score"]) if review_paragraphs else None
        
        # Handle potential key variations between normalised/normalized spelling
        sentence_key = "normalised_score" if "normalised_score" in review_sentences[0] else "normalized_score"
        # Find the most positive and negative sentences within this review
        best_sentence = max(review_sentences, key=lambda x: x[sentence_key]) if review_sentences else None
        worst_sentence = min(review_sentences, key=lambda x: x[sentence_key]) if review_sentences else None
        
        # Calculate comprehensive statistics for this review
        paragraph_scores = [p["normalised_score"] for p in review_paragraphs]
        sentence_scores = [s["normalised_score"] for s in review_sentences]
        
        # Compute average scores for paragraphs and sentences
        avg_paragraph_score = sum(paragraph_scores) / len(paragraph_scores) if paragraph_scores else 0
        avg_sentence_score = sum(sentence_scores) / len(sentence_scores) if sentence_scores else 0
        
        # Compile comprehensive analysis results for this review
        analyzed_review = {
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
        
    
    return analyzed_reviews

def display_review_menu(analyzed_reviews):
    """
    Display an interactive menu of analyzed reviews for user selection.
    Shows preview information and statistics for each review to help user choose.
    
    Args:
        analyzed_reviews (list): List of analyzed review dictionaries from analyze_individual_reviews()
    
    Returns:
        int: Number of available reviews for validation
    
    Process:
        - Displays formatted list of all analyzed reviews
        - Shows preview text, statistics, and sentiment metrics
        - Prompts user for selection to view detailed analysis
        - Provides summary option for overall statistics
    """
    print("\n" + "="*80)
    print("🎯 AVAILABLE REVIEWS FOR DETAILED ANALYSIS")
    print("="*80)
    
    # Display each review with key statistics for user selection
    for i, review_data in enumerate(analyzed_reviews):
        stats = review_data["statistics"]
        print(f"\n📝 Review {i+1}:")
        print(f"   Preview: {review_data['review_text_preview']}")
        print(f"   📊 Stats: {stats['total_paragraphs']} paragraphs, {stats['total_sentences']} sentences")
        print(f"   📈 Avg Score: {stats['avg_paragraph_score']:.3f} (paragraphs), {stats['avg_sentence_score']:.3f} (sentences)")
        print(f"   📏 Score Range: {stats['score_range_paragraphs']:.3f} (paragraphs), {stats['score_range_sentences']:.3f} (sentences)")
    
    print(f"\n🔍 Enter a number (1-{len(analyzed_reviews)}) to analyze a specific review, or 0 to see summary:")
    return len(analyzed_reviews)

def display_detailed_review_analysis(review_data):
    """
    Display comprehensive analysis of a single selected review.
    Shows full text, statistics, and most positive/negative content identification.
    
    Args:
        review_data (dict): Single analyzed review dictionary containing all analysis results
    
    Process:
        - Displays complete review text
        - Shows detailed statistics and sentiment metrics
        - Highlights most positive and negative paragraphs
        - Highlights most positive and negative sentences
        - Provides formatted, readable output for user review
    """
    review_num = review_data["review_index"] + 1
    stats = review_data["statistics"]
    
    print(f"\n" + "="*80)
    print(f"🔍 DETAILED ANALYSIS - REVIEW {review_num}")
    print("="*80)
    
    # Display the complete original review text
    print(f"\n📄 FULL REVIEW TEXT:")
    print(f"{review_data['original_review'].get('review', 'N/A')}")
    
    # Show comprehensive statistics for this review
    print(f"\n📊 REVIEW STATISTICS:")
    print(f"   Total Paragraphs: {stats['total_paragraphs']}")              # Number of sliding windows
    print(f"   Total Sentences: {stats['total_sentences']}")                # Number of individual sentences  
    print(f"   Average Paragraph Score: {stats['avg_paragraph_score']:.3f}")  # Mean sentiment for paragraphs
    print(f"   Average Sentence Score: {stats['avg_sentence_score']:.3f}")    # Mean sentiment for sentences
    print(f"   Paragraph Score Range: {stats['score_range_paragraphs']:.3f}")  # Sentiment variation in paragraphs
    print(f"   Sentence Score Range: {stats['score_range_sentences']:.3f}")    # Sentiment variation in sentences
    
    # Display the most positive content identified
    if review_data["best_paragraph"]:
        best_p = review_data["best_paragraph"]
        print(f"\n🌟 MOST POSITIVE PARAGRAPH (Score: {best_p['normalised_score']:.3f}):")
        print(f"   {best_p['paragraph']}")
        print(f"   📍 Position: Window {best_p['window_position']}, {best_p['sentences_in_window']} sentences")
    
    if review_data["best_sentence"]:
        best_s = review_data["best_sentence"]
        print(f"\n⭐ MOST POSITIVE SENTENCE (Score: {best_s['normalised_score']:.3f}):")
        print(f"   {best_s['sentence']}")
    
    # Display the most negative content identified
    if review_data["worst_paragraph"]:
        worst_p = review_data["worst_paragraph"]
        print(f"\n💔 MOST NEGATIVE PARAGRAPH (Score: {worst_p['normalised_score']:.3f}):")
        print(f"   {worst_p['paragraph']}")
        print(f"   📍 Position: Window {worst_p['window_position']}, {worst_p['sentences_in_window']} sentences")
    
    if review_data["worst_sentence"]:
        worst_s = review_data["worst_sentence"]
        print(f"\n⬇️ MOST NEGATIVE SENTENCE (Score: {worst_s['normalised_score']:.3f}):")
        print(f"   {worst_s['sentence']}")

def display_summary_analysis(analyzed_reviews):
    """
    Display comprehensive summary statistics across all analyzed reviews.
    Provides aggregated insights and overall sentiment analysis results.
    
    Args:
        analyzed_reviews (list): List of analyzed review dictionaries
    
    Process:
        - Calculates aggregate statistics across all reviews
        - Shows distribution of sentiment scores
        - Highlights overall best and worst content found
        - Provides insights into sentiment patterns across the dataset
    """
    print(f"\n" + "="*80)
    print(f"📋 SUMMARY OF ALL {len(analyzed_reviews)} REVIEWS")
    print("="*80)
    
    # Calculate aggregate statistics across all reviews
    total_paragraphs = sum(r["statistics"]["total_paragraphs"] for r in analyzed_reviews)
    total_sentences = sum(r["statistics"]["total_sentences"] for r in analyzed_reviews)
    
    # Collect all sentiment scores for distribution analysis
    all_paragraph_scores = []
    all_sentence_scores = []
    
    for review_data in analyzed_reviews:
        if review_data["best_paragraph"]:
            all_paragraph_scores.append(review_data["best_paragraph"]["normalised_score"])
        if review_data["best_sentence"]:
            # Handle potential key variation (normalised vs normalized)
            score_key = "normalised_score" if "normalised_score" in review_data["best_sentence"] else "normalized_score"
            all_sentence_scores.append(review_data["best_sentence"][score_key])
    
    # Display comprehensive aggregate statistics
    print(f"\n📊 OVERALL STATISTICS:")
    print(f"   Total Paragraphs Analyzed: {total_paragraphs}")                               # Total sliding windows across all reviews
    print(f"   Total Sentences Analyzed: {total_sentences}")                                 # Total individual sentences across all reviews
    print(f"   Average Best Paragraph Score: {sum(all_paragraph_scores)/len(all_paragraph_scores):.3f}")  # Mean of best paragraphs from each review
    print(f"   Average Best Sentence Score: {sum(all_sentence_scores)/len(all_sentence_scores):.3f}")      # Mean of best sentences from each review
    
    # Identify the absolute best and worst content across all reviews
    overall_best_paragraph = max(analyzed_reviews, key=lambda x: x["best_paragraph"]["normalised_score"] if x["best_paragraph"] else -999)
    overall_worst_paragraph = min(analyzed_reviews, key=lambda x: x["worst_paragraph"]["normalised_score"] if x["worst_paragraph"] else 999)
    
    # Highlight the absolute best and worst content found across all reviews
    print(f"\n🏆 OVERALL BEST PARAGRAPH (Review {overall_best_paragraph['review_index'] + 1}):")
    if overall_best_paragraph["best_paragraph"]:
        best = overall_best_paragraph["best_paragraph"]
        print(f"   Score: {best['normalised_score']:.3f}")
        print(f"   Text: {best['paragraph']}")
    
    print(f"\n💀 OVERALL WORST PARAGRAPH (Review {overall_worst_paragraph['review_index'] + 1}):")
    if overall_worst_paragraph["worst_paragraph"]:
        worst = overall_worst_paragraph["worst_paragraph"]
        print(f"   Score: {worst['normalised_score']:.3f}")
        print(f"   Text: {worst['paragraph']}")

if __name__ == "__main__": 
    """
    Main execution block - runs when script is executed directly.
    This block orchestrates the entire sentiment analysis workflow:
    1. Fetches Steam reviews for a specific game
    2. Analyzes each review individually using sliding window technique
    3. Provides interactive menu for users to explore results
    4. Saves detailed analysis to JSON file
    """
    
    # Configuration: Steam game to analyze (Brawlhalla in this case)
    app_id = 315210  # Steam App ID - can be changed to analyze different games

    print("🎮 Fetching Steam reviews...")
    
    # Step 1: Fetch Steam reviews using custom API wrapper module
    # This calls the Steam Web API to get recent English reviews
    raw_reviews = getSteamReviewsData.fetch_steam_reviews(
        app_id=app_id,              # Which game to analyze
        filter_by="recent",         # Get recent reviews (not all-time)
        language="english",         # Only English reviews for text analysis
        day_range=30,              # Reviews from past 30 days only
        review_type="all",         # Both positive and negative reviews
        purchase_type="all",       # All purchase types (free, paid, etc.)
        num_per_page=20           # Limit number of reviews to process
    )

    print(f"📊 Found {len(raw_reviews)} reviews. Analyzing individual reviews...")
    
    # Step 2: Load sentiment dictionary from CSV file
    # This contains words mapped to sentiment scores (positive/negative values)
    sentiment_dict = sentimentDictionary.wordScores()

    # Step 3: Configure sliding window parameters for paragraph analysis
    window_size = 3              # Number of sentences per paragraph window
    step_size = 1               # How many sentences to move window each iteration
    max_reviews_to_analyze = 10 # Limit analysis to 10 reviews for user selection
    
    print(f"🔍 Using sliding window: {window_size} sentences per window, step size {step_size}")
    print(f"📝 Analyzing top {max_reviews_to_analyze} reviews for individual analysis...")
    
    # Step 4: Analyze each review individually to find best/worst content within each
    # This is the core analysis function that applies sliding window technique
    analyzed_reviews = analyze_individual_reviews(
        raw_reviews, sentiment_dict, window_size, step_size, max_reviews_to_analyze
    )
    
    # Step 5: Validate that we have results to work with
    if not analyzed_reviews:
        print("❌ No reviews could be analyzed. Please check your data.")
        exit()
    
    print(f"✅ Successfully analyzed {len(analyzed_reviews)} reviews!")
    
    # Step 6: Interactive user interface loop
    # Allows users to explore individual reviews in detail
    while True:
        try:
            # Display menu of available reviews and get user choice
            max_choice = display_review_menu(analyzed_reviews)
            
            # Get user input for which review to analyze
            choice = input("\nYour choice: ").strip()
            
            # Process user choice
            if choice == "0":
                # Show summary of all analyzed reviews
                display_summary_analysis(analyzed_reviews)
            elif choice.isdigit() and 1 <= int(choice) <= max_choice:
                # Show detailed analysis of selected review
                selected_review = analyzed_reviews[int(choice) - 1]
                display_detailed_review_analysis(selected_review)
            elif choice.lower() in ['quit', 'exit', 'q']:
                # User wants to exit
                print("👋 Goodbye!")
                break
            else:
                # Invalid input handling
                print(f"❌ Invalid choice. Please enter a number between 0 and {max_choice}, or 'quit' to exit.")
            
            # Ask if user wants to continue analyzing
            continue_choice = input(f"\n🔄 Continue analyzing? (y/n): ").strip().lower()
            if continue_choice in ['n', 'no', 'quit', 'exit']:
                print("👋 Goodbye!")
                break
                
        except KeyboardInterrupt:
            # Handle Ctrl+C gracefully
            print("\n👋 Goodbye!")
            break
        except Exception as e:
            # Handle any unexpected errors
            print(f"❌ An error occurred: {e}")
            continue
    
    # Step 7: Save comprehensive results to JSON file for later use
    # This creates a detailed record of all analysis results
    results = {
        "app_id": app_id,
        "total_reviews_fetched": len(raw_reviews),
        "reviews_analyzed": len(analyzed_reviews),
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "sliding_window_config": {
            "window_size": window_size,
            "step_size": step_size
        },
        "analyzed_reviews": analyzed_reviews  # Complete analysis data
    }

    # Write results to JSON file with proper formatting
    with open("individual_review_analysis.json", "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2)

    print(f"💾 Detailed analysis saved to individual_review_analysis.json")