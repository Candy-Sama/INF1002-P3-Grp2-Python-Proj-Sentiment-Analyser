# Import necessary libraries
from flask import Flask, jsonify, render_template
import getSteamReviewsData         
import reviewCleaner               
import sentimentDictionary         
from datetime import datetime
import os

# -----------------------------
# Flask APP INITIALIZATION
# -----------------------------

# Define where to find HTML templates (by default Flask looks for a "templates/" folder)
template_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates')

# Create Flask app, pointing to the template folder
app = Flask(__name__, template_folder=template_dir)

# -----------------------------
# ROUTES
# -----------------------------

@app.route("/")
def index():
    """
    Route for the homepage.
    It simply serves the HTML frontend (index.html).
    """
    return render_template("index.html")  # Located inside the 'templates/' folder


@app.route("/analyze")
def analyze():
    """
    Route for performing live sentiment analysis.
    This function:
    1. Fetches recent Steam reviews for the given app_id.
    2. Cleans each review text.
    3. Scores each review using the sentiment dictionary.
    4. Selects the top positive and negative reviews.
    5. Returns the results as JSON (for the frontend to display).
    """

    # Example Steam game: Brawlhalla (App ID = 315210)
    app_id = 315210

    # Fetch raw reviews (JSON format) using custom function
    raw_reviews = getSteamReviewsData.fetch_steam_reviews(
        app_id,
        language="english",
        filter_by="recent",   # most recent reviews
        num_per_page=100      # fetch 100 reviews per page
    )
    
    # Convert raw reviews into a Pandas DataFrame for easier handling
    df = getSteamReviewsData.reviews_to_dataframe(raw_reviews)

    # Load sentiment dictionary (word → score mapping)
    sentiment_dict = sentimentDictionary.wordScores()

    # List to hold each review's sentiment score
    scored_sentences = []

    # Iterate over reviews (ignore NaN/missing text)
    for review in df['review_text'].dropna().tolist():
        # Clean and normalize the review text
        cleaned = reviewCleaner.reviewFormatter(review)

        # Calculate sentiment score = sum of word scores
        score = sum(sentiment_dict.get(word, 0) for word in cleaned.split())

        # Store result with both text and score
        scored_sentences.append({"sentence": cleaned, "normalized_score": score})

    # Sort reviews: top 10 positive and top 10 negative
    top_positive = sorted(scored_sentences, key=lambda x: x["normalized_score"], reverse=True)[:10]
    top_negative = sorted(scored_sentences, key=lambda x: x["normalized_score"])[:10]

    # Package results for JSON response
    results = {
        "app_id": app_id,
        "total_reviews": len(df),   # how many reviews were processed
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),  # when analysis ran
        "most_positive": top_positive,
        "most_negative": top_negative
    }

    # Return results as JSON so frontend (index.html) can use them
    return jsonify(results)

# -----------------------------
# ENTRY POINT
# -----------------------------
if __name__ == "__main__":
    # Run the Flask app in debug mode (auto reloads on code change, shows detailed errors)
    app.run(debug=True)
