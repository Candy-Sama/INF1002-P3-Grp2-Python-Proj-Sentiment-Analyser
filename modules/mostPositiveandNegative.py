import getSteamReviewsData
import reviewCleaner
import sentimentDictionary
from datetime import datetime
import json
import re # For splitting text into sentences

def score_sentences(reviews, sentiment_dict): #Method to take in reviews and sentiment dictionary, return a list of scored sentences
    scored_sentences = []

    for review in reviews: #Iterate through each review in the list of reviews
        text = review.get("review", "") #Extract the review text, defaulting to an empty string if not found
        if not text:   #Skip empty reviews
            continue

        cleaned = reviewCleaner.reviewFormatter(text) #Clean the review text using the reviewFormatter function from reviewCleaner module
        words = cleaned.split() #Split the cleaned text into individual words
        total_score = sum(sentiment_dict.get(word, 0) for word in words) 

        scored_sentences.append({ #Append the cleaned sentence and its total score to the list
            "sentence": cleaned,
            "normalized_score": total_score
        })

    return scored_sentences

def score_paragraphs(reviews, sentiment_dict, window_size=5, step_size=1): 
    """
    Use sliding window technique to find the most positive paragraphs from reviews.
    
    Variables to take in:
        reviews: List of review dictionaries
        sentiment_dict: Dictionary mapping words to sentiment scores
        window_size: Number of sentences in each window (default: 5)
        step_size: How many sentences to move the window each time (default: 1)
    
    Returns:
        List of scored paragraph windows
    """
    scored_paragraphs = []
    
    for review_idx, review in enumerate(reviews): #Iterate through each review with its index
        text = review.get("review", "") #Extract the review text, defaulting to an empty string if not found
        if not text:
            continue
            
        # Clean the review text
        cleaned_text = reviewCleaner.reviewFormatter(text)
        # Split into sentences (using common sentence delimiters)
        sentences = re.split(r'[.!?]+', cleaned_text)
        sentences = [s.strip() for s in sentences if s.strip()] #For each sentence, strip whitespace and filter out empty strings
        
        # Apply sliding window technique
        for i in range(0, len(sentences) - window_size + 1, step_size): #for each possible window position in the list of sentences
            # Extract window of sentences
            window_sentences = sentences[i:i + window_size] #Get the current window of sentences
            paragraph_text = '. '.join(window_sentences) + '.' #Join sentences into a single paragraph string
            
            # Calculate sentiment score for this window
            words = paragraph_text.lower().split() #makes everything lowercase and splits into words
            window_score = sum(sentiment_dict.get(word, 0) for word in words) #Calculate the raw sentiment score for the window
            
            # Normalize score by number of words to handle different paragraph lengths
            normalized_score = window_score / len(words) if words else 0
            
            scored_paragraphs.append({
                "paragraph": paragraph_text,
                "raw_score": window_score,
                "normalized_score": normalized_score,
                "word_count": len(words),
                "review_index": review_idx,
                "window_position": i,
                "sentences_in_window": len(window_sentences)
            })
    
    return scored_paragraphs

def get_most_positive_paragraphs(scored_paragraphs, top_n=10):
    # Sort by normalized score in descending order
    sorted_paragraphs = sorted(scored_paragraphs, key=lambda x: x["normalized_score"], reverse=True)
    return sorted_paragraphs[:top_n]

def get_most_negative_paragraphs(scored_paragraphs, top_n=10):
    # Sort by normalized score in ascending order
    sorted_paragraphs = sorted(scored_paragraphs, key=lambda x: x["normalized_score"])
    return sorted_paragraphs[:top_n]

if __name__ == "__main__":
    app_id = 315210

    print("🎮 Fetching Steam reviews...")
    # Fetch recent English Steam reviews
    raw_reviews = getSteamReviewsData.fetch_steam_reviews(
        app_id=app_id,
        filter_by="recent",
        language="english",
        day_range=180,
        review_type="all",
        purchase_type="all",
        num_per_page=100
    )

    print(f"📊 Analyzing {len(raw_reviews)} reviews...")
    sentiment_dict = sentimentDictionary.wordScores()

    # Use sliding window technique with configurable parameters
    window_size = 3  # Number of sentences per paragraph window
    step_size = 1    # Move window by 1 sentence each time
    
    print(f"🔍 Using sliding window: {window_size} sentences per window, step size {step_size}")
    
    # Score paragraphs using sliding window technique
    scored_paragraphs = score_paragraphs(raw_reviews, sentiment_dict, window_size, step_size)
    
    print(f"📝 Generated {len(scored_paragraphs)} paragraph windows")

    # Get top positive and negative paragraphs
    top_positive = get_most_positive_paragraphs(scored_paragraphs, top_n=10)
    top_negative = get_most_negative_paragraphs(scored_paragraphs, top_n=10)

    # Also score individual sentences for comparison
    scored_sentences = score_sentences(raw_reviews, sentiment_dict)
    top_positive_sentences = sorted(scored_sentences, key=lambda x: x["normalized_score"], reverse=True)[:10]
    top_negative_sentences = sorted(scored_sentences, key=lambda x: x["normalized_score"])[:10]

    # Save results to JSON for HTML/Flask frontend
    results = {
        "app_id": app_id,
        "total_reviews": len(raw_reviews),
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "sliding_window_config": {
            "window_size": window_size,
            "step_size": step_size,
            "total_windows": len(scored_paragraphs)
        },
        "most_positive_paragraphs": top_positive,
        "most_negative_paragraphs": top_negative,
        "most_positive_sentences": top_positive_sentences,
        "most_negative_sentences": top_negative_sentences
    }

    with open("sentiment_results.json", "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2)

    print(f"✅ Saved results to sentiment_results.json")
    print(f"📈 Most positive paragraph score: {top_positive[0]['normalized_score']:.3f}")
    print(f"📉 Most negative paragraph score: {top_negative[0]['normalized_score']:.3f}")
    
    # Display sample results
    print("\n🌟 MOST POSITIVE PARAGRAPH:")
    print(f"Score: {top_positive[0]['normalized_score']:.3f}")
    print(f"Text: {top_positive[0]['paragraph'][:200]}...")
    
    print("\n💔 MOST NEGATIVE PARAGRAPH:")
    print(f"Score: {top_negative[0]['normalized_score']:.3f}")
    print(f"Text: {top_negative[0]['paragraph'][:200]}...")
