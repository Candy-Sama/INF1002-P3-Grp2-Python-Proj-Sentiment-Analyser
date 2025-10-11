# -----------------------------
# main.py 
# -----------------------------
import sys
import os
import datetime
import webbrowser
from threading import Timer
from flask import Flask, jsonify, render_template, request
from logging import FileHandler,WARNING

# -----------------------------
# Add 'backend/' to Python path
# -----------------------------
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), 'backend')))

from backend import reviewMethods
from backend import createSentimentVisualization
from backend import data_to_frontend

# -----------------------------
# Flask app initialization
# -----------------------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
template_dir = os.path.join(os.path.dirname(__file__), 'frontend', 'templates')
static_dir = os.path.join(os.path.dirname(__file__), 'frontend', 'static')
app = Flask(__name__, template_folder=template_dir, static_folder=static_dir)
file_handler = FileHandler('errorlog.txt')
file_handler.setLevel(WARNING)

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

@app.route("/returnReview", methods=["GET"])
def returnReview():
    # Get parameters from request args
    review_id = request.args.get('review_id')
    app_id = request.args.get('app_id')
    
    print(f"DEBUG: Received review_id={review_id}, app_id={app_id}")
    
    if not review_id or not app_id:
        return jsonify({"error": "Missing review_id or app_id parameter"}), 400
    
    try:
        # Convert review_id to integer
        review_id = int(review_id)
        print(f"DEBUG: Converted review_id to int: {review_id}")
        
        # Get the file path
        file_id = f'steam_reviews_{app_id}.xlsx'
        file_path = os.path.join(BASE_DIR, "data", file_id)
        print(f"DEBUG: Looking for file: {file_path}")
        
        outputList = data_to_frontend.get_reviews(file_path)
        print(f"DEBUG: Found {len(outputList)} reviews")
        print(f"DEBUG: First few review IDs: {[item['review_id'] for item in outputList[:3]]}")

        # Find the specific review
        # Run through the list of dicts to find the one with matching review_id
        result = next((item for item in outputList if int(item["review_id"]) == review_id), None)
        print(f"DEBUG: Found result: {result is not None}")

        if result is None:
            return jsonify({"error": f"Review ID '{review_id}' not found"}), 404
            
        print(f"DEBUG: Processing review text for sentiment analysis...")
        
        # Get Sentence Score
        sentence_to_score = result["review_text"]
        review_length = len(sentence_to_score)
        print(f"DEBUG: Review text length: {review_length}")
        
        # For extremely long reviews (>10000 chars), offer smart truncation
        if review_length > 10000:
            print(f"WARNING: Very long review detected ({review_length} chars). Consider truncation for speed.")
            # Optionally truncate to first 8000 characters for speed
            # sentence_to_score = sentence_to_score[:8000] + "... [truncated for performance]"
        
        # Use optimized analysis functions (original algorithms by Zacc, Ethel, and Mus - performance enhanced)
        try:
            sentence_score, sorted_sentence_score = reviewMethods.sentence_score_calculator(sentence_to_score)
            print(f"DEBUG: Optimized sentence analysis complete")
        except Exception as e:
            print(f"ERROR in sentence_score_calculator: {e}")
            return jsonify({"error": f"Sentence analysis failed: {str(e)}"}), 500

        try:
            # Get Paragraph Score using optimized Sliding Window (Mus's algorithm, performance enhanced)
            scored_paragraphs = reviewMethods.score_paragraphs_SlidingWindow(sentence_to_score)
            print(f"DEBUG: Optimized paragraph analysis complete, found {len(scored_paragraphs)} paragraphs")
        except Exception as e:
            print(f"ERROR in score_paragraphs_SlidingWindow: {e}")
            return jsonify({"error": f"Paragraph analysis failed: {str(e)}"}), 500

        # Extract most positive (first) and most negative (last) paragraphs
        positivePara = scored_paragraphs[0] if scored_paragraphs else None
        negativePara = scored_paragraphs[-1] if scored_paragraphs else None

        print(f"DEBUG: Positive para keys: {positivePara.keys() if positivePara else 'None'}")
        print(f"DEBUG: Negative para keys: {negativePara.keys() if negativePara else 'None'}")

        # Convert numpy int64 to regular int for JSON serialization
        json_safe_result = {
            "review_id": int(result["review_id"]),
            "review_text": result["review_text"],
            "sentence_score": sentence_score,
            "sorted_sentence_score": sorted_sentence_score,
            "most_positive_paragraph_score": positivePara["raw_score"] if positivePara and "raw_score" in positivePara else 0,
            "most_positive_paragraph_text": positivePara["paragraph"] if positivePara and "paragraph" in positivePara else "No positive paragraph found",
            "most_negative_paragraph_text": negativePara["paragraph"] if negativePara and "paragraph" in negativePara else "No negative paragraph found",
            "most_negative_paragraph_score": negativePara["raw_score"] if negativePara and "raw_score" in negativePara else 0
        }

        return jsonify(json_safe_result)
        
    except ValueError as ve:
        print(f"ValueError: {ve}")
        return jsonify({"error": "Invalid review_id format"}), 400
    except Exception as e:
        print(f"Error getting review data: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({"error": "Error loading review text"}), 500


@app.route("/getReviews", methods=["GET"])
def get_reviewsMain():
    # Extract app_id from query parameter
    app_id = request.args.get("app_id")
    if not app_id:
        return jsonify({"error": "Missing required query parameter: app_id"}), 400
    else:
        file_id = f'steam_reviews_{app_id}.xlsx'
        file_path = os.path.join(BASE_DIR, "data", file_id)
        reviewList = data_to_frontend.get_reviews(file_path)

    # Build JSON response
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
    result = {"output": ""}
    # Extract app_id from query parameter
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
    result = [{
        "output_path": output
    }]
    #    "app_id": app_id,
    #    "total_reviews": len(output),
    #    "reviews": output,
    #    "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    #    "most_positive_paragraphs": positive,
    #    "most_negative_paragraphs": negative,
    #    "visualization_path": "output/sentiment_playtime_analysis.png

    return jsonify(result)

def open_browser():
      webbrowser.open_new("http://127.0.0.1:5000")

# -----------------------------
# Entry point
# -----------------------------
if __name__ == "__main__":
    Timer(1, open_browser).start()
    app.run(port=5000)