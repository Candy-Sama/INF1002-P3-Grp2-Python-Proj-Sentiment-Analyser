import pandas as pd
import re
import csv
import os
from getSteamReviewsData import fetch_steam_reviews, reviews_to_dataframe

def load_sentiment_dictionary():
    """Load sentiment dictionary from CSV file."""
    sentiment_dict = {}
    file_path = os.path.join('..', 'data', 'sentiment_dictionary.csv')
    
    try:
        with open(file_path, 'r', newline='', encoding='utf-8-sig') as csvfile:
            for row in csv.reader(csvfile):
                if len(row) >= 2:
                    sentiment_dict[row[0].lower()] = float(row[1])
        print(f"Loaded {len(sentiment_dict)} sentiment words")
    except Exception as e:
        print(f"Error loading sentiment dictionary: {e}")
        return {}
    
    return sentiment_dict

def score_sentence(sentence, sentiment_dict):
    """Calculate sentiment score for a sentence."""
    words = re.sub(r'[^a-zA-Z\s]', '', sentence.lower()).split()
    total_score = sum(sentiment_dict.get(word, 0) for word in words)
    word_count = len(words)
    
    return {
        'sentence': sentence.strip(),
        'score': total_score,
        'normalized_score': total_score / max(word_count, 1),
        'word_count': word_count
    }

def find_extreme_sentences(df, sentiment_dict, top_n=10):
    """Find most positive and negative sentences."""
    all_sentences = []
    
    print("Analyzing sentences...")
    for idx, row in df.iterrows():
        review_text = row.get('review_text', '')
        if not review_text:
            continue
            
        # Split into sentences
        sentences = [s.strip() for s in re.split(r'[.!?]+', review_text) 
                    if s.strip() and len(s.strip()) > 10]
        
        for sentence in sentences:
            sentence_data = score_sentence(sentence, sentiment_dict)
            sentence_data.update({
                'review_id': row.get('review_id'),
                'recommended': row.get('recommended'),
                'review_index': idx
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

def display_results(most_positive, most_negative):
    """Display the results."""
    print(f"\n=== TOP {len(most_positive)} MOST POSITIVE SENTENCES ===")
    for i, s in enumerate(most_positive, 1):
        print(f"{i}. Score: {s['normalized_score']:.3f} | \"{s['sentence'][:80]}...\"")
    
    print(f"\n=== TOP {len(most_negative)} MOST NEGATIVE SENTENCES ===")
    for i, s in enumerate(most_negative, 1):
        print(f"{i}. Score: {s['normalized_score']:.3f} | \"{s['sentence'][:80]}...\"")

def main():
    """Main function."""
    print("=== STEAM REVIEW SENTIMENT ANALYSIS ===")
    
    app_id = 315210
    
    # Fetch and process reviews
    raw_reviews = fetch_steam_reviews(app_id=app_id, filter_by='recent', 
                                     language='english', num_per_page=100)
    df = reviews_to_dataframe(raw_reviews)
    print(f"Analyzing {len(df)} reviews")
    
    # Load sentiment dictionary and analyze
    sentiment_dict = load_sentiment_dictionary()
    if not sentiment_dict:
        return
    
    most_positive, most_negative = find_extreme_sentences(df, sentiment_dict, 10)
    display_results(most_positive, most_negative)
    
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
