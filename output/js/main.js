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
             html += `<div class="review-card">
                          <div class="review-meta">
                              <span onclick="runSentimentAnalysis()" id="review_id" data-value="${index}">${review}</span>
                          </div>
                      </div>`;
        })//<div class="review-text">${p.sentence}</div>


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

        contentDiv.innerHTML = html;

    } catch (error) {
        status.innerHTML = '❌ Error running analysis!';
        contentDiv.innerHTML = '<p style="color: #e74c3c;">❌ Failed to load results</p>';
        console.error(error);
    }
}

async function runSentimentAnalysis() {
    const reviewId = document.getElementById('review_id')
    const reviewIdVal = event.target.dataset.value;
    console.log(reviewIdVal)
    try {
        const response = await fetch(`/reviewId?review_id=${reviewIdVal}`);
        const data = await response.json();
        console.log(data)
    } catch (error) {
        console.error(error)
    }
}