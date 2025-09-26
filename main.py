# -----------------------------
# main.py
# -----------------------------
import sys
import os
import datetime
from flask import Flask, jsonify, render_template, request

# -----------------------------
# Add 'modules/' to Python path
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
template_dir = os.path.join(os.path.dirname(__file__), 'output', 'templates')
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
    - Fetches reviews from last 10 days.
    - Cleans and processes reviews.
    - Runs sliding window sentiment analysis.
    - Generates playtime visualization.
    - Returns JSON results.
    """
    # 1️⃣ Extract app_id from query parameter
    app_id = request.args.get("app_id", type=int)
    if not app_id:
        return jsonify({"error": "Missing required query parameter: app_id"}), 400

    # 2️⃣ Fetch reviews from the last 10 days
    reviews = getSteamReviewsData.fetch_steam_reviews(
        app_id,
        filter_by='recent',
        language='english',
        day_range=10,  # last 10 days
        num_per_page=200
    )

    if not reviews:
        return jsonify({"error": f"No recent reviews found for App ID '{app_id}'"}), 404

    # 3️⃣ Clean and preprocess reviews
    cleaned_reviews = [reviewCleaner.reviewFormatter(r) for r in reviews]

    # 4️⃣ Load sentiment dictionary
    sentiment_dict = sentimentDictionary.wordScores()

    # 5️⃣ Sliding window sentiment analysis
    positive, negative = sliding_window_demo.run_sliding_window(cleaned_reviews, sentiment_dict)

    # 6️⃣ Save reviews to Excel for visualization
    df_reviews = getSteamReviewsData.reviews_to_dataframe(reviews)
    excel_path = f'steam_reviews_{app_id}.xlsx'
    df_reviews.to_excel(excel_path, index=False)

    # 7️⃣ Generate playtime-based sentiment visualization
    createSentimentVisualization.create_sentiment_playtime_visualization()

    # 8️⃣ Build JSON response
    result = {
        "app_id": app_id,
        "total_reviews": len(reviews),
        "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "most_positive_paragraphs": positive,
        "most_negative_paragraphs": negative,
        "visualization_path": "output/sentiment_playtime_analysis.png"
    }

    return jsonify(result)


# -----------------------------
# Entry point
# -----------------------------
if __name__ == "__main__":
    app.run(debug=True)
