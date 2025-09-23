# -----------------------------
# server.py
# -----------------------------
from flask import Flask, jsonify, render_template
import getSteamReviewsData
import reviewCleaner
import sentimentDictionary
import mostpositiveandnegative  # new module for sliding window scoring
from datetime import datetime
import os

# -----------------------------
# Flask APP INITIALIZATION
# -----------------------------
template_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates')
app = Flask(__name__, template_folder=template_dir)

# -----------------------------
# ROUTES
# -----------------------------
@app.route("/")
def index():
    """Serve the homepage HTML"""
    return render_template("index.html")


@app.route("/analyze")
def analyze():
    """Perform live Steam review sentiment analysis with sliding window"""
    app_id = 315210  # Example game: Brawlhalla

    # 1) Fetch reviews
    raw_reviews = getSteamReviewsData.fetch_steam_reviews(
        app_id,
        language="english",
        filter_by="recent",
        num_per_page=100
    )

    # 2) Convert to DataFrame for easier handling
    df = getSteamReviewsData.reviews_to_dataframe(raw_reviews)

    # 3) Load sentiment dictionary
    sentiment_dict = sentimentDictionary.wordScores()

    # 4) Prepare review list for analysis
    reviews_list = df.to_dict(orient="records")

    # 5) Run sliding window analysis on each review
    analyzed_reviews = mostpositiveandnegative.analyse_individual_reviews(
        reviews_list,
        sentiment_dict,
        window_size=3,  # number of sentences per window
        step_size=1,
        max_reviews=100  # limit to 100 reviews for performance
    )

    # 6) Extract top positive and negative paragraphs across all reviews
    all_paragraphs = []
    for review in analyzed_reviews:
        all_paragraphs.extend(review["all_paragraphs"])

    top_positive = sorted(all_paragraphs, key=lambda x: x["normalised_score"], reverse=True)[:10]
    top_negative = sorted(all_paragraphs, key=lambda x: x["normalised_score"])[:10]

    # 7) Prepare JSON response
    results = {
        "app_id": app_id,
        "total_reviews": len(df),
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "most_positive_paragraphs": top_positive,
        "most_negative_paragraphs": top_negative
    }

    return jsonify(results)


# -----------------------------
# ENTRY POINT
# -----------------------------
if __name__ == "__main__":
    app.run(debug=True)
