# -----------------------------
# main.py
# -----------------------------
import sys
import os
from flask import Flask, jsonify, render_template, request
import datetime
import requests

# -----------------------------
# Add 'modules/' folder to Python path
# -----------------------------
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), 'modules')))

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
template_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), 'output', 'templates'))
app = Flask(__name__, template_folder=template_dir)

# -----------------------------
# Helper function to get Steam app_id from game name
# -----------------------------
def get_app_id_from_name(game_name):
    """
    Use Steam Store search API to resolve game name to app_id.
    Returns app_id if found, otherwise None.
    """
    search_url = "https://store.steampowered.com/api/storesearch/"
    params = {
        "term": game_name,
        "l": "english",
        "cc": "US"
    }
    try:
        resp = requests.get(search_url, params=params)
        resp.raise_for_status()
        data = resp.json()
        if data.get("items"):
            return data["items"][0]["id"]  # take first search result
    except Exception as e:
        print("Error resolving app_id:", e)
    return None

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
    API endpoint: /analyze?game_name=XXXX

    Steps:
    1. Extract game name from query.
    2. Resolve to app_id.
    3. Fetch reviews.
    4. Clean/process reviews.
    5. Run sentiment analysis.
    6. Return JSON results.
    """
    # 1️⃣ Get game_name from query
    game_name = request.args.get("game_name", type=str)
    if not game_name:
        return jsonify({"error": "Missing required query parameter: game_name"}), 400

    # 2️⃣ Resolve game_name to app_id
    app_id = get_app_id_from_name(game_name)
    if not app_id:
        return jsonify({"error": f"Could not find app_id for game '{game_name}'"}), 404

    # 3️⃣ Fetch raw reviews
    reviews = getSteamReviewsData.fetch_steam_reviews(app_id, num_per_page=200)
    if not reviews:
        return jsonify({"error": f"Could not fetch reviews for app_id {app_id}"}), 500

    # 4️⃣ Clean/process reviews
    cleaned_reviews = [reviewCleaner.reviewFormatter(r) for r in reviews]

    # 5️⃣ Load sentiment dictionary
    sentiment_dict = sentimentDictionary.wordScores()

    # 6️⃣ Run sliding window sentiment analysis
    positive, negative = sliding_window_demo.run_sliding_window(cleaned_reviews, sentiment_dict)

    # 7️⃣ Build JSON response
    result = {
        "game_name": game_name,
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
    app.run(debug=True)
