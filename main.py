# -----------------------------
# main.py 
# -----------------------------
import sys
import os
import datetime
import webbrowser
from threading import Timer
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
from modules import createSentimentVisualization
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
#Ethel's codes
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
        #run through the list of dicts to find the one with matching review_id
        result = next((item for item in outputList if item["review_id"] == review_id), None)
        if result is None:
            return jsonify({"error": f"Review ID '{review_id}' not found"}), 404
        else:
            # Convert numpy int64 to regular int for JSON serialization
            json_safe_result = {
                "review_id": int(result["review_id"]),
                "review_text": result["review_text"],
                "segmented_sentences": reviewMethods.format_review(result["review_text"])
            }
            print(f"segmented_sentences: {json_safe_result['segmented_sentences']}") #debug
            return jsonify(json_safe_result)
    except ValueError:
        return jsonify({"error": "Invalid review_id format"}), 400
    except Exception as e:
        print(f"Error getting review data: {e}")
        return jsonify({"error": "Error loading review text"}), 500


@app.route("/getReviews", methods=["GET"])
def get_reviewsMain():
    #Extract app_id from query parameter
    app_id = request.args.get("app_id")
    if not app_id:
        return jsonify({"error": "Missing required query parameter: app_id"}), 400
    else:
        file_id = f'steam_reviews_{app_id}.xlsx'
        file_path = os.path.join(BASE_DIR, "data", file_id)
        reviewList = data_to_frontend.get_reviews(file_path)

    #Build JSON response
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


@app.route("/summaryVisualisation", methods=["GET"])
def summaryVisualisation():
    #Extract app_id from query parameter
    app_id = request.args.get("app_id", type=int)
    if not app_id:
        return jsonify({"error": "Missing required query parameter: app_id"}), 400
    else:
        file_id = f'steam_reviews_{app_id}.xlsx'
        file_path = os.path.join(BASE_DIR, "data", file_id)
        output = createSentimentVisualization.create_sentiment_playtime_visualization(file_path)
        
        # Show the plot
        # plt.show()
        
        # Save detailed data
        # summary_data.to_csv('output/sentiment_by_playtime_detailed.csv', index=False)
        # print("\nDetailed data saved to: output/sentiment_by_playtime_detailed.csv")

        # output = data_to_frontend.get_reviews(file_path)

    # 8️⃣ Build JSON response
    result = {
        "output_path": output
    #    "app_id": app_id,
    #    "total_reviews": len(output),
    #    "reviews": output,
    #    "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    #    "most_positive_paragraphs": positive,
    #    "most_negative_paragraphs": negative,
    #    "visualization_path": "output/sentiment_playtime_analysis.png"
    }

    return jsonify(result)

def open_browser():
      webbrowser.open_new("http://127.0.0.1:5000")

# -----------------------------
# Entry point
# -----------------------------
if __name__ == "__main__":
    Timer(1, open_browser).start()
    app.run(port=5000)