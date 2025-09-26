# -----------------------------
# server.py
# -----------------------------
import sys
import os
from flask import Flask, jsonify, render_template, request
import datetime

# -----------------------------
# Add parent folder to Python path
# -----------------------------
# This allows importing modules from 'modules/' folder
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'modules')))
import getSteamReviewsData
import reviewCleaner
import reviewScorer
import sentimentDictionary
import sliding_window_demo
import additionalDataPoints
import createSentimentVisualization


# -----------------------------
# Flask app initialization
# -----------------------------
# templates folder is one level above 'output/'
template_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'templates'))
app = Flask(__name__, template_folder=template_dir)

# -----------------------------
# Routes
# -----------------------------
@app.route("/")
def index():
    """Serve the homepage"""
    return render_template("index.html")


@app.route("/analyze", methods=["GET"])
def analyze_reviews():
    """
    API endpoint: /analyze?app_id=XXXX

    - Accepts a Steam App ID as a query parameter.
    - Fetches reviews for that App ID.
    - Cleans and processes reviews.
    - Runs sentiment analysis (including sliding window).
    - Returns JSON results.
    """
    # 1️⃣ Extract app_id from query parameter
    app_id = request.args.get("app_id", type=int)
    if not app_id:
        return jsonify({"error": "Missing required query parameter: app_id"}), 400

    # 2️⃣ Fetch raw review data
    reviews = getSteamReviewsData.fetch_steam_reviews(app_id, num_per_page=200)
    if not reviews:
        return jsonify({"error": f"Could not fetch reviews for app_id {app_id}"}), 500

    # 3️⃣ Clean/preprocess reviews
    cleaned_reviews = [reviewCleaner.reviewFormatter(r) for r in reviews]

    # 4️⃣ Load sentiment dictionary
    sentiment_dict = sentimentDictionary.wordScores()

    # 5️⃣ Sliding window sentiment analysis
    positive, negative = sliding_window_demo.run_sliding_window(cleaned_reviews, sentiment_dict)

    # 6️⃣ Build JSON response
    result = {
        "app_id": app_id,
        "total_reviews": len(reviews),
        "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "most_positive_paragraphs": positive,
        "most_negative_paragraphs": negative
    }

    return jsonify(result)


# -----------------------------
# Entry point
# -----------------------------
if __name__ == "__main__":
    # Debug mode for development
    app.run(debug=True)
