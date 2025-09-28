// Main JavaScript functions for Steam Review Sentiment Analysis

async function runGetReviews() {
    const status = document.getElementById('analysisStatus');
    const resultsDiv = document.getElementById('liveResults');
    const contentDiv = document.getElementById('resultsContent');
    const vizImg = document.getElementById('visualization');
    const appId = document.getElementById('app_id').value;

    if (!appId) { 
        status.innerHTML = '❌ Please enter a valid App ID!'; 
        return; 
    }

    status.innerHTML = '⏳ Running sentiment analysis on server...';
    resultsDiv.style.display = 'block';
    contentDiv.innerHTML = '⏳ Loading...';
    vizImg.style.display = 'none';

    try {
        const response = await fetch(`/analyze?app_id=${appId}`);
        const data = await response.json();
        console.log(data)

        if (data.error) {
            status.innerHTML = '❌ ' + data.error;
            contentDiv.innerHTML = '';
            return;
        }

        status.innerHTML = '✅ Analysis complete! Click into each review to analyse the sentiment!';

        // Show visualization
        // vizImg.src = data.visualization_path + '?t=' + new Date().getTime();
        // vizImg.style.display = 'block';

        let html = `<p><strong>App ID:</strong> ${data.app_id} | <strong>Total Reviews:</strong> ${data.total_reviews} | <strong>Timestamp:</strong> ${data.timestamp}</p>`;

        // Print out reviews
        html += `<h3 style="color: #00000;">Reviews</h3>`;
        data.reviews.forEach((review, index) => {
            console.log(`Main.js Review Index is ${index}`); // For debugging
             html += `<div class="review-card">
                          <div class="review-meta">
                              <a href="/reviewAnalyser?review_id=${index}&app_id=${appId}"> <!-- (Mus) go to review analyser with the value ${index} -->
                                <span id="review_id_${index}" data-value="${index}">${review}</span>
                              </a>
                          </div>
                      </div>`;
        })

        contentDiv.innerHTML = html;

    } catch (error) {
        status.innerHTML = '❌ Error running analysis!';
        contentDiv.innerHTML = '<p style="color: #e74c3c;">❌ Failed to load results</p>';
        console.error(error);
    }
}


//Function to call from the json the review ID and display the results
async function runSentimentAnalysis(elementID, review_id) { //Edited by Mus
    // Get review ID from clicked element's data-value attribute
    const reviewId = review_id;
    console.log('Element ID:', elementID, 'Review ID:', reviewId); //For testing
    
    const element = document.getElementById(elementID);
    if (!element) {
        console.error(`Element with ID '${elementID}' not found!`);
        return;
    }
    try {
        //Call from the sentiment_results.json the review ID and display the results
        const response = await fetch(`/reviewAnalyser?review_id=${reviewId}`);
        const data = await response.json();
        console.log('Received data:', data);
        
        // Update the element with the received data
        if (data.error) {
            element.innerHTML = `<p>❌ Error: ${data.error}</p>`;
        } else {
            // Display the sentiment analysis results
            element.innerHTML = `
                <p>✅ Sentiment analysis completed!</p>
                <p><strong>Review ID:</strong> ${reviewId}</p>
                <p><strong>Sentiment:</strong> ${data.sentiment || 'Unknown'}</p>
                <p><strong>Confidence Score:</strong> ${data.confidence_score || 'N/A'}</p>
                <p><strong>Review Text:</strong> ${data.review_text || 'No text available'}</p>
            `;
        }
    } catch (error) {
        console.error('Fetch error:', error);
        element.innerHTML = `<p>❌ Error loading sentiment analysis</p>`;
    }
}

// Function to update review analysis with timeout (Mus code)
function updateReviewAnalysis(elementID, review_id, timeOut = 3000) {
    console.log(`Starting timeout for element: ${elementID}, review: ${review_id}, delay: ${timeOut}ms`);
    
    const reviewAnalysisTimeout = setTimeout(() => { //Create a timeout and store its ID
        console.log(`Timeout fired! Calling runSentimentAnalysis...`);
        // call the method to update the review analysis - pass elementID (string), not element (DOM object)
        runSentimentAnalysis(elementID, review_id);
    }, timeOut); // (default: 3000ms)
    
    return reviewAnalysisTimeout; // Return timeout ID in case you need to clear it
}

//ethel's code
// <div class="review-text">${p.sentence}</div>


        // Most positive paragraphs
        // html += `<h3 style="color: #27ae60;">🌟 Top Positive Paragraphs</h3>`;
        // data.most_positive_paragraphs.forEach(p => {
        //     html += `<div class="review-card positive">
        //                 <div class="review-meta">
        //                     <span class="sentiment-badge positive">😊 ${p.normalized_score.toFixed(3)}</span>
        //                 </div>
        //                 <div class="review-text">${p.sentence}</div>
        //             </div>`;
        // });

        // // Most negative paragraphs
        // html += `<h3 style="color: #e74c3c;">💔 Top Negative Paragraphs</h3>`;
        // data.most_negative_paragraphs.forEach(p => {
        //     html += `<div class="review-card negative">
        //                 <div class="review-meta">
        //                     <span class="sentiment-badge negative">😞 ${p.normalized_score.toFixed(3)}</span>
        //                 </div>
        //                 <div class="review-text">${p.sentence}</div>
        //             </div>`;
        // });