#!/usr/bin/env python3
"""
Standalone demonstration of the sliding window technique for sentiment analysis.
This shows how the score_paragraphs function works without requiring external dependencies.
"""

import re

def demo_sliding_window():
    """
    Demonstrate how the sliding window technique works with sample text.
    """
    sample_text = """This game is amazing. The graphics are stunning and beautiful. 
    The gameplay is smooth and responsive. However, some bugs exist in the system. 
    The story is compelling and engaging. Overall, I highly recommend this game to everyone."""
    
    print("🔍 SLIDING WINDOW DEMONSTRATION")
    print("=" * 50)
    print(f"Sample text: {sample_text}")
    print()
    
    # Split into sentences
    sentences = re.split(r'[.!?]+', sample_text)
    sentences = [s.strip() for s in sentences if s.strip()]
    
    print(f"📝 Split into {len(sentences)} sentences:")
    for i, sentence in enumerate(sentences):
        print(f"  {i+1}: {sentence}")
    print()
    
    # Create sample sentiment dictionary
    sample_sentiment = {
        'amazing': 3.0, 'stunning': 2.5, 'beautiful': 2.0, 'smooth': 1.5, 
        'responsive': 1.0, 'bugs': -2.0, 'compelling': 2.0, 'engaging': 1.5,
        'recommend': 2.5, 'highly': 1.0, 'game': 0.5, 'graphics': 0.5,
        'gameplay': 0.5, 'story': 0.5, 'overall': 0.0
    }
    
    window_size = 3
    print(f"🪟 Sliding window size: {window_size} sentences")
    print()
    
    scored_windows = []
    
    # Apply sliding window
    for i in range(len(sentences) - window_size + 1):
        window_sentences = sentences[i:i + window_size]
        paragraph_text = '. '.join(window_sentences) + '.'
        
        # Calculate score
        words = paragraph_text.lower().split()
        raw_score = sum(sample_sentiment.get(word, 0) for word in words)
        normalized_score = raw_score / len(words) if words else 0
        
        scored_windows.append({
            'window_id': i + 1,
            'paragraph': paragraph_text,
            'raw_score': raw_score,
            'normalized_score': normalized_score,
            'word_count': len(words)
        })
        
        print(f"Window {i+1} (sentences {i+1}-{i+window_size}):")
        print(f"  Text: {paragraph_text}")
        print(f"  Raw Score: {raw_score:.2f}")
        print(f"  Normalized Score: {normalized_score:.3f}")
        print(f"  Word Count: {len(words)}")
        print()
    
    # Find most positive and negative windows
    most_positive = max(scored_windows, key=lambda x: x['normalized_score'])
    most_negative = min(scored_windows, key=lambda x: x['normalized_score'])
    
    print("🌟 MOST POSITIVE WINDOW:")
    print(f"  Window {most_positive['window_id']}")
    print(f"  Score: {most_positive['normalized_score']:.3f}")
    print(f"  Text: {most_positive['paragraph']}")
    print()
    
    print("💔 MOST NEGATIVE WINDOW:")
    print(f"  Window {most_negative['window_id']}")
    print(f"  Score: {most_negative['normalized_score']:.3f}")
    print(f"  Text: {most_negative['paragraph']}")
    print()
    
    print("📊 All windows ranked by sentiment:")
    sorted_windows = sorted(scored_windows, key=lambda x: x['normalized_score'], reverse=True)
    for i, window in enumerate(sorted_windows):
        print(f"  {i+1}. Window {window['window_id']}: {window['normalized_score']:.3f}")

def demonstrate_different_window_sizes():
    """
    Show how different window sizes affect the results.
    """
    sample_reviews = [
        "This game is terrible. The graphics are awful. But the story is amazing!",
        "Great gameplay mechanics. Some minor bugs though. Overall very enjoyable experience.",
        "Horrible controls. Frustrating gameplay. Waste of money. Not recommended at all."
    ]
    
    sentiment_dict = {
        'terrible': -3.0, 'awful': -2.5, 'amazing': 3.0, 'great': 2.0,
        'bugs': -1.5, 'enjoyable': 2.5, 'horrible': -3.0, 'frustrating': -2.0,
        'waste': -2.5, 'recommended': 2.0, 'not': -0.5
    }
    
    print("\n" + "="*60)
    print("🔧 TESTING DIFFERENT WINDOW SIZES")
    print("="*60)
    
    for window_size in [2, 3, 4]:
        print(f"\n🪟 Window Size: {window_size}")
        print("-" * 30)
        
        all_windows = []
        
        for review_idx, review_text in enumerate(sample_reviews):
            sentences = re.split(r'[.!?]+', review_text)
            sentences = [s.strip() for s in sentences if s.strip()]
            
            for i in range(len(sentences) - window_size + 1):
                window_sentences = sentences[i:i + window_size]
                paragraph_text = '. '.join(window_sentences) + '.'
                
                words = paragraph_text.lower().split()
                score = sum(sentiment_dict.get(word, 0) for word in words)
                normalized_score = score / len(words) if words else 0
                
                all_windows.append({
                    'review_idx': review_idx + 1,
                    'paragraph': paragraph_text,
                    'normalized_score': normalized_score
                })
        
        # Show top positive and negative
        top_positive = max(all_windows, key=lambda x: x['normalized_score'])
        top_negative = min(all_windows, key=lambda x: x['normalized_score'])
        
        print(f"Most Positive: {top_positive['normalized_score']:.3f}")
        print(f"  {top_positive['paragraph']}")
        print(f"Most Negative: {top_negative['normalized_score']:.3f}")
        print(f"  {top_negative['paragraph']}")

if __name__ == "__main__":
    demo_sliding_window()
    demonstrate_different_window_sizes()