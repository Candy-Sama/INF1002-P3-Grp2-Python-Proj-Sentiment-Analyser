import getSteamReviewsData
import reviewCleaner
import sentimentDictionary
from datetime import datetime
import json

def score_sentences(reviews, sentiment_dict):
    scored_sentences = []

    for review in reviews:
        text = review.get("review", "")
        if not text:
            continue

        cleaned = reviewCleaner.reviewFormatter(text)
        words = cleaned.split()
        total_score = sum(sentiment_dict.get(word, 0) for word in words)

        scored_sentences.append({
            "sentence": cleaned,
            "normalized_score": total_score
        })

    return scored_sentences

if __name__ == "__main__":
    app_id = 315210

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

    sentiment_dict = sentimentDictionary.wordScores()

    scored_sentences = score_sentences(raw_reviews, sentiment_dict)

    # Sort top positive and negative sentences
    top_positive = sorted(scored_sentences, key=lambda x: x["normalized_score"], reverse=True)[:10]
    top_negative = sorted(scored_sentences, key=lambda x: x["normalized_score"])[:10]

    # Save results to JSON for HTML/Flask frontend
    results = {
        "app_id": app_id,
        "total_reviews": len(raw_reviews),
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "most_positive": top_positive,
        "most_negative": top_negative
    }

    with open("sentiment_results.json", "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2)

    print(f"✅ Saved results to sentiment_results.json | {len(raw_reviews)} reviews analyzed")
