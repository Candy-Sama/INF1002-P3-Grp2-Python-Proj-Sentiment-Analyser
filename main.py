# -----------------------------
# main.py
# -----------------------------
import sys
import os
import datetime
from unittest import result
from flask import Flask, jsonify, render_template, request, g

# -----------------------------
# Add 'modules/' to Python path
# -----------------------------
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), 'modules')))

from modules import fetch_steam_data
from modules import reviewMethods
from modules import sentiment_dict
from modules import additionalDataPoints
# from modules import createSentimentVisualization
from modules import most_positive_negative
from modules import data_to_frontend

# -----------------------------
# Flask app initialization
# -----------------------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
template_dir = os.path.join(os.path.dirname(__file__), 'output')
static_dir = os.path.join(os.path.dirname(__file__), 'output')
app = Flask(__name__, template_folder=template_dir, static_folder=static_dir)

# -----------------------------
# Routes
# -----------------------------
@app.route("/")
def index():
    """Serve the homepage"""
    return render_template("index.html")

@app.route("/reviewAnalyser") # Edited by Mus
def reviewAnalyser():
    """Serve the review analyser page"""
    review_id = request.args.get("review_id", type=int)
    app_id = request.args.get("app_id", type=int)
    print(f"Received review_id: {review_id}, app_id: {app_id}")
    
    # Debug: Check if values are None
    if review_id is None:
        print("WARNING: review_id is None!")
    if app_id is None:
        print("WARNING: app_id is None!")
    
    # Pass the parameters to the template (correct syntax with named parameters)
    return render_template("reviewAnalyser.html",
                           review_id=review_id,
                           app_id=app_id)

@app.route("/returnReview")
def returnReview():
    # Get parameters from request args
    review_id = request.args.get('review_id')
    app_id = request.args.get('app_id')
    
    if not review_id or not app_id:
        return jsonify({"error": "Missing review_id or app_id parameter"}), 400
    
    try:
        # Convert review_id to integer
        review_id = int(review_id)
        
        # Get the file path
        file_id = f'steam_reviews_{app_id}.xlsx'
        file_path = os.path.join(BASE_DIR, "data", file_id)
        outputList = data_to_frontend.get_reviews(file_path)

        #find the specific review
        result = next((item for item in outputList if item["review_id"] == review_id), None)
        if result is None:
            return jsonify({"error": f"Review ID '{review_id}' not found"}), 404
        else:
            # Convert numpy int64 to regular int for JSON serialization
            json_safe_result = {
                "review_id": int(result["review_id"]),
                "review_text": result["review_text"]
            }
            return jsonify(json_safe_result)
    except ValueError:
        return jsonify({"error": "Invalid review_id format"}), 400
    except Exception as e:
        print(f"Error getting review data: {e}")
        return jsonify({"error": "Error loading review text"}), 500


@app.route("/analyze", methods=["GET"])
def get_reviews():
    # 1️⃣ Extract app_id from query parameter
    app_id = request.args.get("app_id")
    if not app_id:
        return jsonify({"error": "Missing required query parameter: app_id"}), 400
    else:
        file_id = f'steam_reviews_{app_id}.xlsx'
        file_path = os.path.join(BASE_DIR, "data", file_id)
        reviewList = data_to_frontend.get_reviews(file_path)

    # 8️⃣ Build JSON response
    result = {
        "app_id": app_id,
        "total_reviews": len(reviewList),
        "review_id": [int(review["review_id"]) for review in reviewList], # add review_id list, convert to int
        "reviews": [str(review["review_text"]) for review in reviewList], # add review text list
        "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    #    "most_positive_paragraphs": positive,
    #    "most_negative_paragraphs": negative,
    #    "visualization_path": "output/sentiment_playtime_analysis.png"
    }

    return jsonify(result)

# -----------------------------
# Entry point
# -----------------------------
if __name__ == "__main__":
    app.run(debug=True)




    # 2️⃣ Fetch reviews from the last 10 days
    # reviews = getSteamReviewsData.fetch_steam_reviews(
    #     app_id,
    #     filter_by='recent',
    #     language='english',
    #     day_range=10,  # last 10 days
    #     num_per_page=200
    # )

    # if not reviews:
    #     return jsonify({"error": f"No recent reviews found for App ID '{app_id}'"}), 404

    # # 3️⃣ Clean and preprocess reviews
    # cleaned_reviews = [reviewMethods.reviewFormatter(r) for r in reviews]

    # # 4️⃣ Load sentiment dictionary
    # sentiment_dictionary = sentiment_dict.wordScores()

    # # 5️⃣ Sliding window sentiment analysis
    # positive, negative = sliding_window_demo.run_sliding_window(cleaned_reviews, sentiment_dict)

    # # 6️⃣ Save reviews to Excel for visualization
    # df_reviews = getSteamReviewsData.reviews_to_dataframe(reviews)
    # excel_path = f'steam_reviews_{app_id}.xlsx'
    # df_reviews.to_excel(excel_path, index=False)

    # # 7️⃣ Generate playtime-based sentiment visualization
    # # createSentimentVisualization.create_sentiment_playtime_visualization()
