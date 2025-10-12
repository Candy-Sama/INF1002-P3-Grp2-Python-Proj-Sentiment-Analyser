// =============================================================================
// ACTIVE CODE - Main JavaScript functions for Steam Review Sentiment Analysis
// =============================================================================

// =============================================================================
// INDEX.HTML FUNCTIONS - Main Dashboard Functions (Created by Ethel)
// =============================================================================

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

    status.innerHTML = '<div class="loading-indicator"><span class="loading-hourglass">⧗</span><span>Running advanced sentiment analysis on Steam reviews...</span></div>';
    status.className = 'status-indicator loading';
    resultsDiv.style.display = 'block';
    contentDiv.innerHTML = '<div class="loading-indicator"><span class="loading-hourglass">⧗</span><span>Processing review data...</span></div>';
    vizImg.style.display = 'none';

    try {
        const response = await fetch(`/getReviews?app_id=${appId}`);
        const data = await response.json();
        console.log('Received data:', data);

        if (data.error) {
            status.innerHTML = '❌ ' + data.error;
            contentDiv.innerHTML = '';
            return;
        }

        status.innerHTML = '✅ <strong>Analysis Complete!</strong> Click on any review below for detailed sentiment analysis';
        status.className = 'status-indicator success';

        let html = `<p><strong>App ID:</strong> ${data.app_id} | <strong>Total Reviews:</strong> ${data.total_reviews} | <strong>Timestamp:</strong> ${data.timestamp}</p>`;

        // Print out reviews
        html += `<h3 style="color: #00000;">Reviews</h3>`;
        data.reviews.forEach((review, index) => {
            const reviewId = data.review_id[index]; // Get the corresponding review ID
            console.log(`Main.js Review Index is ${index}, Review ID is ${reviewId}`); // For debugging
             html += `<div class="review-card">
                          <div class="review-meta">
                              <a href="/reviewAnalyser?review_id=${reviewId}&app_id=${appId}"> <!-- (Mus) go to review analyser with the review ID -->
                                <span id="review_id_${index}" data-value="${reviewId}">${review}</span>
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

// =============================================================================
// REVIEWANALYSER.HTML FUNCTIONS - Deep Analysis Functions (Created by Mus)
// =============================================================================

//Function to call from the json the review ID and display the results
async function runSentimentAnalysis(reviewID, appID, originalReviewSection, sentenceAnalysisSection, mostPositiveSentenceSection, mostNegativeSentenceSection, mostPositiveParagraphSection, mostNegativeParagraphSection) { //Mus
    // Get review ID from clicked element's data-value attribute
    const reviewId = reviewID;
    console.log('Original Review Section:', originalReviewSection, 'Review ID:', reviewId); //For debug

    const originalReviewElement = document.getElementById(originalReviewSection);
    const sentenceAnalysisElement = document.getElementById(sentenceAnalysisSection);
    const mostPositiveSentenceElement = document.getElementById(mostPositiveSentenceSection);
    const mostNegativeSentenceElement = document.getElementById(mostNegativeSentenceSection);
    const mostPositiveParagraphElement = document.getElementById(mostPositiveParagraphSection);
    const mostNegativeParagraphElement = document.getElementById(mostNegativeParagraphSection);

    if (!originalReviewElement) {
        console.error(`Original Review Element with ID '${originalReviewSection}' not found!`);
        return;
    }
    try {
        // Call from the excel sheet the review ID and display the results
        const response = await fetch(`/returnReview?review_id=${reviewID}&app_id=${appID}`);
        const data = await response.json();
        console.log('Received data:', data);
        
        // Update the element with the received data
        if (data.error) {
            originalReviewElement.innerHTML = `<p>❌ Error: ${data.error}</p>`;
        } 
        else {
            // Display the sentiment analysis results
            let sentence_score = data.sentence_score
            let sorted_sentence_score = data.sorted_sentence_score
            let most_negative_paragraph_score = data.most_negative_paragraph_score
            let most_positive_paragraph_score = data.most_positive_paragraph_score
            let most_negative_paragraph_text = data.most_negative_paragraph_text
            let most_positive_paragraph_text = data.most_positive_paragraph_text

            // 1. Original Review Content Section
            originalReviewElement.innerHTML = `
                <div class="analysis-complete-badge">
                    <span class="success-icon">✅</span>
                    <strong>Analysis Complete!</strong>
                </div>
                <div class="review-content-display">
                    <h4 class="content-subtitle">📄 Complete Review Text</h4>
                    <div class="review-text-container">
                        <p class="review-text">${data.review_text || 'No review text available'}</p>
                    </div>
                    <div class="review-stats">
                        <span class="stat-item">📊 <strong>Sentences Analyzed:</strong> ${sentence_score.length}</span>
                        <span class="stat-item">🔢 <strong>Review ID:</strong> ${data.review_id}</span>
                    </div>
                </div>
            `;
            
            // 2. Detailed Sentence Analysis Section
            let sentenceListHTML = `
                <div class="sentence-analysis-header">
                    <h4 class="content-subtitle">🔍 Individual Sentence Breakdown</h4>
                    <p class="analysis-description">Each sentence analyzed for sentiment with numerical scores</p>
                </div>
                <div class="sentence-list">
            `;

            for (let i = 0; i < sentence_score.length; i++) {
                const score = data.sentence_score[i][1];
                const sentimentClass = score > 0 ? 'positive-sentiment' : score < 0 ? 'negative-sentiment' : 'neutral-sentiment';
                const sentimentIcon = score > 0 ? '😊' : score < 0 ? '😞' : '😐';
                
                sentenceListHTML += `
                    <div class="sentence-item ${sentimentClass}">
                        <div class="sentence-header">
                            <span class="sentence-number">Sentence ${i + 1}</span>
                            <span class="sentiment-score ${sentimentClass}">${sentimentIcon} Score: ${score.toFixed(3)}</span>
                        </div>
                        <div class="sentence-text">${data.sentence_score[i][0] || 'No text available'}</div>
                    </div>
                `;
            }
            sentenceListHTML += `</div>`;
            sentenceAnalysisElement.innerHTML = sentenceListHTML;

            // 3. Most Positive Sentence Section
            mostPositiveSentenceElement.innerHTML = `
                <div class="extreme-sentiment-content">
                    <div class="sentiment-badge positive-badge">
                        <span class="badge-icon">🌟</span>
                        <span class="badge-text">Highest Positive Sentence</span>
                    </div>
                    <div class="sentiment-details">
                        <div class="score-display positive-score">+${data.sorted_sentence_score[0][1].toFixed(3)}</div>
                        <div class="sentence-content">"${data.sorted_sentence_score[0][0] || 'No text available'}"</div>
                    </div>
                </div>
            `;

            // 4. Most Negative Sentence Section
            mostNegativeSentenceElement.innerHTML = `
                <div class="extreme-sentiment-content">
                    <div class="sentiment-badge negative-badge">
                        <span class="badge-icon">💔</span>
                        <span class="badge-text">Highest Negative Sentence</span>
                    </div>
                    <div class="sentiment-details">
                        <div class="score-display negative-score">${data.sorted_sentence_score[sorted_sentence_score.length - 1][1].toFixed(3)}</div>
                        <div class="sentence-content">"${data.sorted_sentence_score[sorted_sentence_score.length - 1][0] || 'No text available'}"</div>
                    </div>
                </div>
            `;

            // 5. Most Positive Paragraph (Sliding Window) Section
            mostPositiveParagraphElement.innerHTML = `
                <div class="paragraph-analysis-content">
                    <div class="analysis-method-badge">
                        <span class="method-icon">🎯</span>
                        <span class="method-name">Sliding Window Analysis</span>
                    </div>
                    <div class="paragraph-result positive-paragraph">
                        <div class="paragraph-score-header">
                            <span class="context-label">Most Positive Paragraph</span>
                            <span class="paragraph-score positive-score">Score: +${most_positive_paragraph_score?.toFixed(3) || '0.000'}</span>
                        </div>
                        <div class="paragraph-content">
                            <p class="paragraph-text">${most_positive_paragraph_text || 'No positive paragraph found'}</p>
                        </div>
                    </div>
                </div>
            `;

            // 6. Most Negative Paragraph (Sliding Window) Section
            mostNegativeParagraphElement.innerHTML = `
                <div class="paragraph-analysis-content">
                    <div class="analysis-method-badge">
                        <span class="method-icon">🎯</span>
                        <span class="method-name">Sliding Window Analysis</span>
                    </div>
                    <div class="paragraph-result negative-paragraph">
                        <div class="paragraph-score-header">
                            <span class="context-label">Most Negative Paragraph</span>
                            <span class="paragraph-score negative-score">Score: ${most_negative_paragraph_score?.toFixed(3) || '0.000'}</span>
                        </div>
                        <div class="paragraph-content">
                            <p class="paragraph-text">${most_negative_paragraph_text || 'No negative paragraph found'}</p>
                        </div>
                    </div>
                </div>
            `;

        }
    } catch (error) {
        console.error('Fetch error:', error);
        originalReviewElement.innerHTML = `<p>❌ Error loading sentiment analysis</p>`;
    }
}

// =============================================================================
// INDEX.HTML FUNCTIONS - Summary Visualization (Team Collaboration)
// =============================================================================

async function runSummarizeReviews() {
    const status = document.getElementById('analysisStatus');
    const resultsDiv = document.getElementById('liveResults');
    const contentDiv = document.getElementById('resultsContentSummary');
    const vizImg = document.getElementById('visualization');
    const appId = document.getElementById('app_id').value;

    if (!appId) { 
        status.innerHTML = '❌ Please enter a valid App ID!'; 
        return; 
    }

    status.innerHTML = '<div class="loading-indicator"><span class="loading-hourglass">⧗</span><span>Running summary analysis on server...</span></div>';
    resultsDiv.style.display = 'block';
    contentDiv.innerHTML = '<div class="loading-indicator"><span class="loading-hourglass">⧗</span><span>Generating summary visualization...</span></div>';
    vizImg.style.display = 'none';

    try {
        console.log("Before const response")
        const response = await fetch(`/summaryVisualisation?app_id=${appId}`);
        console.log(response)
        console.log("After const response")
        const data = await response.json();
        console.log(data)

        if (data.error) {
            status.innerHTML = '❌ ' + data.error;
            contentDiv.innerHTML = '';
            return;
        }

        status.innerHTML = '✅ Summary complete!';

         // 1. Create the image element
        const newImage = document.createElement("img");

        // 2. Set the image source
        newImage.src = "../static/css/sentiment_playtime_analysis.png";

        // 3. Set the alt text and style for accessibility and viewing
        newImage.alt = "A summary of the Steam Reviews";
        
        newImage.style.width = "1000px"

        // 4. Get the container element where you want to add the image
        const container = document.getElementById("imageContainer");

        // 5. Append the image to the container
        if (!container.hasChildNodes()) {
        container.appendChild(newImage)};

        contentDiv.innerHTML = "";

    } catch (error) {
        status.innerHTML = '❌ Error running summary!';
        contentDiv.innerHTML = '<p style="color: #e74c3c;">❌ Failed to load summary</p>';
        console.error(error);
    }
}