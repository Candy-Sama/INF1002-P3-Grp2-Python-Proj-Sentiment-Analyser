import pandas as pd
import re
import csv
import os
import requests
from datetime import datetime
import sentimentDictionary

def score_sentence(sentence, sentiment_dict):
    """Calculate sentiment score for a sentence."""
    words = re.sub(r'[^a-zA-Z\s]', '', sentence.lower()).split()
    word_count = len(words)
    
    return {
        'sentence': sentence.strip(),
        'score': 0,
        'normalized_score': 0,
        'word_count': word_count
    }

def find_extreme_sentences(reviews, sentiment_dict, top_n=10):
    """Find most positive and negative sentences."""
    all_sentences = []
    
    print("Analyzing sentences...")
    for i, review in enumerate(reviews):
        review_text = review.get('review', '')
        if not review_text:
            continue
            
        # Split into sentences
        sentences = [s.strip() for s in re.split(r'[.!?]+', review_text) 
                    if s.strip() and len(s.strip()) > 10]
        
        for sentence in sentences:
            sentence_data = score_sentence(sentence, sentiment_dict)
            sentence_data.update({
                'review_id': review.get('recommendationid'),
                'recommended': review.get('voted_up'),
                'review_index': i
            })
            all_sentences.append(sentence_data)
    
    # Filter sentences with meaningful scores
    meaningful = [s for s in all_sentences if s['score'] != 0]
    print(f"Found {len(meaningful)} sentences with sentiment")
    
    # Sort by normalized score
    sorted_sentences = sorted(meaningful, key=lambda x: x['normalized_score'])
    
    most_negative = sorted_sentences[:top_n]
    most_positive = sorted_sentences[-top_n:][::-1]
    
    return most_positive, most_negative

def main():
    """Main function."""
    print("=== STEAM REVIEW SENTIMENT ANALYSIS ===")
    
    app_id = 315210
    
    # Fetch reviews directly from Steam API
    base_url = f"https://store.steampowered.com/appreviews/{app_id}"
    params = {
        'json': 1,
        'filter': 'recent',
        'language': 'english',
        'day_range': 180,
        'review_type': 'all',
        'purchase_type': 'all',
        'num_per_page': 100,
        'cursor': '*'
    }
    
    reviews = []
    cursor = '*'
    
    while True:
        params['cursor'] = cursor
        resp = requests.get(base_url, params=params)
        data = resp.json()
        
        batch = data.get('reviews', [])
        if not batch:
            break
            
        reviews.extend(batch)
        cursor = data.get('cursor')
        if not cursor or cursor == params['cursor']:
            break
    
    print(f"Fetched {len(reviews)} reviews")
    
    # Get sentiment dictionary from sentimentDictionary.py
    sentiment_dict = sentimentDictionary.sentimentDict
    
    most_positive, most_negative = find_extreme_sentences(reviews, sentiment_dict, 10)
    
    # Display results
    print(f"\n=== TOP {len(most_positive)} MOST POSITIVE SENTENCES ===")
    for i, s in enumerate(most_positive, 1):
        print(f"{i}. Score: {s['normalized_score']:.3f} | \"{s['sentence'][:80]}...\"")
    
    print(f"\n=== TOP {len(most_negative)} MOST NEGATIVE SENTENCES ===")
    for i, s in enumerate(most_negative, 1):
        print(f"{i}. Score: {s['normalized_score']:.3f} | \"{s['sentence'][:80]}...\"")
    
    # Save to CSV
    output_dir = os.path.join('..', 'output')
    os.makedirs(output_dir, exist_ok=True)
    
    all_sentences = most_positive + most_negative
    df_results = pd.DataFrame(all_sentences)
    csv_file = os.path.join(output_dir, f'extreme_sentences_{app_id}.csv')
    df_results.to_csv(csv_file, index=False)
    print(f"\nResults saved to: {csv_file}")

if __name__ == "__main__":
    main()
