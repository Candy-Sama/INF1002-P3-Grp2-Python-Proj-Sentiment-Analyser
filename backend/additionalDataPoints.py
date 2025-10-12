"""
Additional Data Points Analysis for Steam Reviews
Analyzes reviewer characteristics and their impact on sentiment:
- Reviewer's time played (playtime_at_review_h)
- Number of games reviewed by user (num_reviews_by_user)
- Playtime during review
- How many people found it funny (votes_funny)
- Whether game was purchased or received for free (steam_purchase, received_for_free)
"""

# =============================================================================
# UNUSED CODE - Complete file preserved for future use
# =============================================================================

import pandas as pd
import matplotlib.pyplot as plt
import json

def load_steam_reviews_data():
    """Load the Steam reviews data from Excel file"""
    try:
        df = pd.read_excel('steam_reviews_315210.xlsx')
        print(f"[SUCCESS] Loaded {len(df)} reviews from Steam data")
        return df
    except FileNotFoundError:
        print("Error: steam_reviews_315210.xlsx not found. Please ensure the file exists.")
        return None

def analyze_reviewer_playtime_patterns(df):
    """Analyze sentiment patterns based on reviewer's playtime"""
    print("\n" + "="*60)
    print("REVIEWER PLAYTIME ANALYSIS")
    print("="*60)
    
    # Convert playtime to hours (assuming it's in minutes)
    df['playtime_hours'] = df['playtime_at_review_h'] / 60
    df['sentiment_score'] = df['recommended'].astype(int)
    
    # Create playtime categories
    playtime_bins = [0, 1, 5, 10, 25, 50, 100, 500, float('inf')]
    playtime_labels = ['0-1h', '1-5h', '5-10h', '10-25h', '25-50h', '50-100h', '100-500h', '500h+']
    
    df['playtime_category'] = pd.cut(df['playtime_hours'], 
                                   bins=playtime_bins, 
                                   labels=playtime_labels, 
                                   right=False)
    
    # Analyze sentiment by playtime
    playtime_analysis = df.groupby('playtime_category', observed=True).agg({
        'sentiment_score': ['mean', 'count', 'std'],
        'playtime_hours': ['mean', 'median'],
        'votes_helpful': 'mean',
        'votes_funny': 'mean'
    }).round(3)
    
    playtime_analysis.columns = ['sentiment_avg', 'review_count', 'sentiment_std', 
                               'avg_hours', 'median_hours', 'avg_helpful_votes', 'avg_funny_votes']
    
    print("Sentiment by Playtime Categories:")
    # Format the output for better display
    for category, row in playtime_analysis.iterrows():
        print(f"{category:>10}: {row['sentiment_avg']:.3f} sentiment | "
              f"{int(row['review_count']):>5} reviews | "
              f"{row['avg_hours']:>6.1f}h avg | "
              f"{row['avg_helpful_votes']:>6.1f} helpful | "
              f"{row['avg_funny_votes']:>4.1f} funny")
    
    return playtime_analysis

def analyze_reviewer_experience(df):
    """Analyze sentiment based on reviewer's experience (number of games reviewed)"""
    print("\n" + "="*60)
    print("REVIEWER EXPERIENCE ANALYSIS")
    print("="*60)
    
    df['sentiment_score'] = df['recommended'].astype(int)
    
    # Create experience bins based on number of reviews written
    experience_bins = [0, 1, 5, 10, 25, 50, 100, float('inf')]
    experience_labels = ['1 review', '2-5 reviews', '6-10 reviews', '11-25 reviews', 
                        '26-50 reviews', '51-100 reviews', '100+ reviews']
    
    df['reviewer_experience'] = pd.cut(df['num_reviews_by_user'], 
                                     bins=experience_bins, 
                                     labels=experience_labels, 
                                     right=False)
    
    # Analyze sentiment by reviewer experience
    experience_analysis = df.groupby('reviewer_experience', observed=True).agg({
        'sentiment_score': ['mean', 'count'],
        'num_reviews_by_user': ['mean', 'median'],
        'playtime_at_review_h': 'mean',
        'votes_helpful': 'mean',
        'num_games_owned': 'mean'
    }).round(3)
    
    experience_analysis.columns = ['sentiment_avg', 'review_count', 'avg_reviews_written', 
                                 'median_reviews_written', 'avg_playtime', 'avg_helpful_votes', 'avg_games_owned']
    
    print("Sentiment by Reviewer Experience:")
    # Format the output for better display
    for experience, row in experience_analysis.iterrows():
        print(f"{experience:>15}: {row['sentiment_avg']:.3f} sentiment | "
              f"{int(row['review_count']):>5} reviews | "
              f"{row['avg_reviews_written']:>5.1f} avg reviews | "
              f"{row['avg_games_owned']:>6.1f} games")
    
    return experience_analysis

def analyze_humor_factor(df):
    """Analyze relationship between funny votes and sentiment"""
    print("\n" + "="*60)
    print("HUMOR FACTOR ANALYSIS")
    print("="*60)
    
    df['sentiment_score'] = df['recommended'].astype(int)
    
    # Create funny votes categories
    df['has_funny_votes'] = df['votes_funny'] > 0
    df['funny_category'] = pd.cut(df['votes_funny'], 
                                bins=[-1, 0, 1, 5, 10, float('inf')], 
                                labels=['No funny votes', '1 funny vote', '2-5 funny votes', 
                                       '6-10 funny votes', '10+ funny votes'])
    
    # Analyze sentiment by humor
    humor_analysis = df.groupby('funny_category', observed=True).agg({
        'sentiment_score': ['mean', 'count'],
        'votes_funny': ['mean', 'max'],
        'votes_helpful': 'mean',
        'playtime_at_review_h': 'mean'
    }).round(3)
    
    humor_analysis.columns = ['sentiment_avg', 'review_count', 'avg_funny_votes', 
                            'max_funny_votes', 'avg_helpful_votes', 'avg_playtime']
    
    print("Sentiment by Funny Votes:")
    # Format the output for better display
    for category, row in humor_analysis.iterrows():
        print(f"{category:>15}: {row['sentiment_avg']:.3f} sentiment | "
              f"{int(row['review_count']):>5} reviews | "
              f"{row['avg_funny_votes']:>4.1f} funny avg | "
              f"{row['avg_helpful_votes']:>6.1f} helpful")
    
    # Correlation analysis
    funny_correlation = df['votes_funny'].corr(df['sentiment_score'])
    print(f"\nCorrelation between funny votes and sentiment: {funny_correlation:.3f}")
    
    return humor_analysis

def analyze_purchase_vs_free(df):
    """Analyze sentiment difference between purchased vs free games"""
    print("\n" + "="*60)
    print("PURCHASE VS FREE ANALYSIS")
    print("="*60)
    
    df['sentiment_score'] = df['recommended'].astype(int)
    
    # Create purchase categories
    df['acquisition_type'] = 'Unknown'
    df.loc[df['steam_purchase'] == True, 'acquisition_type'] = 'Steam Purchase'
    df.loc[df['received_for_free'] == True, 'acquisition_type'] = 'Received Free'
    df.loc[(df['steam_purchase'] == False) & (df['received_for_free'] == False), 'acquisition_type'] = 'External Purchase'
    
    # Analyze sentiment by acquisition type
    purchase_analysis = df.groupby('acquisition_type').agg({
        'sentiment_score': ['mean', 'count', 'std'],
        'playtime_at_review_h': ['mean', 'median'],
        'votes_helpful': 'mean',
        'votes_funny': 'mean',
        'num_games_owned': 'mean'
    }).round(3)
    
    purchase_analysis.columns = ['sentiment_avg', 'review_count', 'sentiment_std',
                               'avg_playtime', 'median_playtime', 'avg_helpful_votes', 
                               'avg_funny_votes', 'avg_games_owned']
    
    print("Sentiment by Acquisition Type:")
    # Format the output for better display
    for acq_type, row in purchase_analysis.iterrows():
        print(f"{acq_type:>15}: {row['sentiment_avg']:.3f} sentiment | "
              f"{int(row['review_count']):>5} reviews | "
              f"{row['avg_playtime']:>6.1f}min avg | "
              f"{row['avg_games_owned']:>6.1f} games")
    
    return purchase_analysis

def analyze_games_owned_impact(df):
    """Analyze how the number of games owned affects review sentiment"""
    print("\n" + "="*60)
    print("GAMES OWNED IMPACT ANALYSIS")
    print("="*60)
    
    df['sentiment_score'] = df['recommended'].astype(int)
    
    # Create games owned categories
    games_bins = [0, 10, 50, 100, 250, 500, 1000, float('inf')]
    games_labels = ['1-10 games', '11-50 games', '51-100 games', '101-250 games', 
                   '251-500 games', '501-1000 games', '1000+ games']
    
    df['games_owned_category'] = pd.cut(df['num_games_owned'], 
                                      bins=games_bins, 
                                      labels=games_labels, 
                                      right=False)
    
    # Analyze sentiment by games owned
    games_analysis = df.groupby('games_owned_category', observed=True).agg({
        'sentiment_score': ['mean', 'count'],
        'num_games_owned': ['mean', 'median'],
        'playtime_at_review_h': 'mean',
        'num_reviews_by_user': 'mean'
    }).round(3)
    
    games_analysis.columns = ['sentiment_avg', 'review_count', 'avg_games_owned', 
                            'median_games_owned', 'avg_playtime', 'avg_reviews_written']
    
    print("Sentiment by Number of Games Owned:")
    # Format the output for better display
    for category, row in games_analysis.iterrows():
        print(f"{category:>15}: {row['sentiment_avg']:.3f} sentiment | "
              f"{int(row['review_count']):>5} reviews | "
              f"{row['avg_games_owned']:>6.1f} games avg | "
              f"{row['avg_reviews_written']:>5.1f} reviews written")
    
    return games_analysis

def create_comprehensive_visualization(df):
    """Create comprehensive visualizations for all additional data points"""
    print("\n" + "="*60)
    print("CREATING COMPREHENSIVE VISUALIZATIONS")
    print("="*60)
    
    # Prepare data
    df['sentiment_score'] = df['recommended'].astype(int)
    df['playtime_hours'] = df['playtime_at_review_h'] / 60
    
    # Create subplots
    fig, axes = plt.subplots(2, 3, figsize=(20, 12))
    fig.suptitle('Steam Reviews: Additional Data Points Analysis', fontsize=16, fontweight='bold')
    
    # 1. Sentiment by Playtime
    playtime_bins = [0, 1, 5, 10, 25, 50, 100, 500, float('inf')]
    playtime_labels = ['0-1h', '1-5h', '5-10h', '10-25h', '25-50h', '50-100h', '100-500h', '500h+']
    df['playtime_cat'] = pd.cut(df['playtime_hours'], bins=playtime_bins, labels=playtime_labels, right=False)
    
    playtime_sentiment = df.groupby('playtime_cat', observed=True)['sentiment_score'].mean()
    axes[0,0].bar(range(len(playtime_sentiment)), playtime_sentiment.values, color='skyblue')
    axes[0,0].set_title('Sentiment by Playtime')
    axes[0,0].set_xticks(range(len(playtime_sentiment)))
    axes[0,0].set_xticklabels(playtime_sentiment.index, rotation=45)
    axes[0,0].set_ylabel('Positive Sentiment Ratio')
    
    # 2. Sentiment by Games Owned
    games_bins = [0, 50, 100, 250, 500, float('inf')]
    games_labels = ['1-50', '51-100', '101-250', '251-500', '500+']
    df['games_cat'] = pd.cut(df['num_games_owned'], bins=games_bins, labels=games_labels, right=False)
    
    games_sentiment = df.groupby('games_cat', observed=True)['sentiment_score'].mean()
    axes[0,1].bar(range(len(games_sentiment)), games_sentiment.values, color='lightgreen')
    axes[0,1].set_title('Sentiment by Games Owned')
    axes[0,1].set_xticks(range(len(games_sentiment)))
    axes[0,1].set_xticklabels(games_sentiment.index, rotation=45)
    axes[0,1].set_ylabel('Positive Sentiment Ratio')
    
    # 3. Sentiment by Purchase Type
    df['purchase_type'] = 'Steam Purchase'
    df.loc[df['received_for_free'] == True, 'purchase_type'] = 'Free'
    df.loc[(df['steam_purchase'] == False) & (df['received_for_free'] == False), 'purchase_type'] = 'External'
    
    purchase_sentiment = df.groupby('purchase_type')['sentiment_score'].mean()
    axes[0,2].bar(range(len(purchase_sentiment)), purchase_sentiment.values, color='lightcoral')
    axes[0,2].set_title('Sentiment by Purchase Type')
    axes[0,2].set_xticks(range(len(purchase_sentiment)))
    axes[0,2].set_xticklabels(purchase_sentiment.index, rotation=45)
    axes[0,2].set_ylabel('Positive Sentiment Ratio')
    
    # 4. Funny Votes Distribution
    axes[1,0].hist(df['votes_funny'], bins=50, alpha=0.7, color='orange')
    axes[1,0].set_title('Distribution of Funny Votes')
    axes[1,0].set_xlabel('Funny Votes')
    axes[1,0].set_ylabel('Frequency')
    axes[1,0].set_xlim(0, 20)  # Focus on lower range
    
    # 5. Playtime vs Sentiment Scatter
    sample_df = df.sample(n=min(1000, len(df)))  # Sample for performance
    scatter = axes[1,1].scatter(sample_df['playtime_hours'], sample_df['sentiment_score'], 
                               alpha=0.5, c=sample_df['votes_funny'], cmap='viridis')
    axes[1,1].set_title('Playtime vs Sentiment (colored by funny votes)')
    axes[1,1].set_xlabel('Playtime (hours)')
    axes[1,1].set_ylabel('Sentiment (0=negative, 1=positive)')
    axes[1,1].set_xlim(0, 100)  # Focus on reasonable range
    plt.colorbar(scatter, ax=axes[1,1], label='Funny Votes')
    
    # 6. Review Experience Impact
    exp_bins = [0, 5, 10, 25, 50, float('inf')]
    exp_labels = ['1-5', '6-10', '11-25', '26-50', '50+']
    df['exp_cat'] = pd.cut(df['num_reviews_by_user'], bins=exp_bins, labels=exp_labels, right=False)
    
    exp_sentiment = df.groupby('exp_cat', observed=True)['sentiment_score'].mean()
    axes[1,2].bar(range(len(exp_sentiment)), exp_sentiment.values, color='mediumpurple')
    axes[1,2].set_title('Sentiment by Reviewer Experience')
    axes[1,2].set_xticks(range(len(exp_sentiment)))
    axes[1,2].set_xticklabels(exp_sentiment.index, rotation=45)
    axes[1,2].set_ylabel('Positive Sentiment Ratio')
    
    plt.tight_layout()
    plt.savefig('output/additional_datapoints_analysis.png', dpi=300, bbox_inches='tight')
    print("[SUCCESS] Comprehensive visualization saved to: output/additional_datapoints_analysis.png")
    
    # Show the plot
    plt.show()
    
    return fig

def generate_summary_report(df):
    """Generate a comprehensive summary report of all additional data points"""
    print("\n" + "="*60)
    print("COMPREHENSIVE SUMMARY REPORT")
    print("="*60)
    
    df['sentiment_score'] = df['recommended'].astype(int)
    df['playtime_hours'] = df['playtime_at_review_h'] / 60
    
    report = {
        'dataset_overview': {
            'total_reviews': len(df),
            'overall_positive_sentiment': df['sentiment_score'].mean(),
            'avg_playtime_hours': df['playtime_hours'].mean(),
            'avg_games_owned': df['num_games_owned'].mean(),
            'avg_funny_votes': df['votes_funny'].mean()
        },
        'key_insights': []
    }
    
    # Purchase type insights
    purchase_stats = df.groupby(df['steam_purchase'])['sentiment_score'].mean()
    if True in purchase_stats.index and False in purchase_stats.index:
        steam_sentiment = purchase_stats[True]
        other_sentiment = purchase_stats[False]
        report['key_insights'].append(f"Steam purchases show {steam_sentiment:.1%} positive sentiment vs {other_sentiment:.1%} for other sources")
    
    # Free game insights
    if df['received_for_free'].any():
        free_sentiment = df[df['received_for_free'] == True]['sentiment_score'].mean()
        paid_sentiment = df[df['received_for_free'] == False]['sentiment_score'].mean()
        report['key_insights'].append(f"Free games: {free_sentiment:.1%} positive vs Paid games: {paid_sentiment:.1%} positive")
    
    # Playtime insights
    high_playtime = df[df['playtime_hours'] > 25]['sentiment_score'].mean()
    low_playtime = df[df['playtime_hours'] <= 1]['sentiment_score'].mean()
    report['key_insights'].append(f"High playtime (25h+): {high_playtime:.1%} positive vs Low playtime (≤1h): {low_playtime:.1%} positive")
    
    # Funny votes correlation
    funny_corr = df['votes_funny'].corr(df['sentiment_score'])
    report['key_insights'].append(f"Funny votes correlation with sentiment: {funny_corr:.3f}")
    
    # Games owned impact
    many_games = df[df['num_games_owned'] > 250]['sentiment_score'].mean()
    few_games = df[df['num_games_owned'] <= 50]['sentiment_score'].mean()
    report['key_insights'].append(f"Many games owned (250+): {many_games:.1%} vs Few games (≤50): {few_games:.1%}")
    
    print(f"Total Reviews Analyzed: {report['dataset_overview']['total_reviews']:,}")
    print(f"Overall Positive Sentiment: {report['dataset_overview']['overall_positive_sentiment']:.1%}")
    print(f"Average Playtime: {report['dataset_overview']['avg_playtime_hours']:.1f} hours")
    print(f"Average Games Owned: {report['dataset_overview']['avg_games_owned']:.0f}")
    print(f"Average Funny Votes: {report['dataset_overview']['avg_funny_votes']:.2f}")
    
    print("\nKey Insights:")
    for i, insight in enumerate(report['key_insights'], 1):
        print(f"{i}. {insight}")
    
    # Save report as JSON
    with open('output/additional_datapoints_report.json', 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2)
    
    print("\n[SUCCESS] Full report saved to: output/additional_datapoints_report.json")
    return report

def main():
    """Main function to run all additional data points analysis"""
    print("Steam Reviews - Additional Data Points Analysis")
    print("=" * 60)
    
    # Load data
    df = load_steam_reviews_data()
    if df is None:
        return
    
    print(f"Analyzing {len(df)} reviews with the following data points:")
    print("- Reviewer's time played (playtime_at_review_h)")
    print("- Number of games reviewed by user (num_reviews_by_user)")
    print("- How many people found it funny (votes_funny)")
    print("- Purchase vs free status (steam_purchase, received_for_free)")
    print("- Number of games owned (num_games_owned)")
    
    # Run all analyses
    playtime_analysis = analyze_reviewer_playtime_patterns(df)
    experience_analysis = analyze_reviewer_experience(df)
    humor_analysis = analyze_humor_factor(df)
    purchase_analysis = analyze_purchase_vs_free(df)
    games_analysis = analyze_games_owned_impact(df)
    
    # Create visualizations
    create_comprehensive_visualization(df)
    
    # Generate summary report
    report = generate_summary_report(df)
    
    print("\n" + "="*60)
    print("ANALYSIS COMPLETE!")
    print("[SUCCESS] All additional data points analyzed")
    print("[SUCCESS] Visualizations created")
    print("[SUCCESS] Summary report generated")
    print("="*60)
    
    return {
        'playtime_analysis': playtime_analysis,
        'experience_analysis': experience_analysis,
        'humor_analysis': humor_analysis,
        'purchase_analysis': purchase_analysis,
        'games_analysis': games_analysis,
        'summary_report': report
    }

if __name__ == "__main__":
    results = main()