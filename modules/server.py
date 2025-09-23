
from flask import Flask, jsonify, render_template
import getSteamReviewsData
import reviewCleaner
import sentimentDictionary
from datetime import datetime
import os

# Python backend using Flask to serve a simple web page and provide an API endpoint for sentiment analysis.
# Set the template folder to point to the correct location
template_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates')
app = Flask(__name__, template_folder=template_dir)

@app.route("/")
def index():
    return render_template("index.html")  # your HTML file in templates/

@app.route("/analyze")
def analyze():
    app_id = 315210  # Example: Brawlhalla
    raw_reviews = getSteamReviewsData.fetch_steam_reviews(
        app_id, language="english", filter_by="recent", num_per_page=100
    )
    
    df = getSteamReviewsData.reviews_to_dataframe(raw_reviews)

    sentiment_dict = sentimentDictionary.wordScores()

    scored_sentences = []
    for review in df['review_text'].dropna().tolist():
        cleaned = reviewCleaner.reviewFormatter(review)
        score = sum(sentiment_dict.get(word, 0) for word in cleaned.split())
        scored_sentences.append({"sentence": cleaned, "normalized_score": score})

    # Sort top positive/negative sentences
    top_positive = sorted(scored_sentences, key=lambda x: x["normalized_score"], reverse=True)[:10]
    top_negative = sorted(scored_sentences, key=lambda x: x["normalized_score"])[:10]

    results = {
        "app_id": app_id,
        "total_reviews": len(df),
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "most_positive": top_positive,
        "most_negative": top_negative
    }

    return jsonify(results)


if __name__ == "__main__":
    app.run(debug=True)
