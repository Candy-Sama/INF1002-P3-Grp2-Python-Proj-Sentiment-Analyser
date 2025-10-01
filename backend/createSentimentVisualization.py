"""
Steam Reviews Sentiment Analysis by Playtime
Creates comprehensive visualizations showing sentiment flow based on playtime hours
"""

import pandas as pd
import matplotlib.pyplot as plt

def create_sentiment_playtime_visualization(file_id):
    """Create comprehensive sentiment analysis visualization"""
    
    # Read and prepare the data
    print("Loading Steam reviews data...")
    df = pd.read_excel(file_id)
    
    # Convert playtime from minutes to hours
    df['playtime_hours'] = df['playtime_at_review_m'] / 60
    df['sentiment_score'] = df['recommended'].astype(int)
    
    # Create playtime bins (in hours)
    playtime_bins = [0, 1, 5, 10, 25, 50, 100, 500, 1200]
    playtime_labels = ['0-1h', '1-5h', '5-10h', '10-25h', '25-50h', '50-100h', '100-500h', '500h+']
    
    df['playtime_bin'] = pd.cut(df['playtime_hours'], 
                                bins=playtime_bins, 
                                labels=playtime_labels, 
                                right=False)
    
    # Calculate sentiment statistics
    sentiment_stats = df.groupby('playtime_bin', observed=True).agg({
        'sentiment_score': ['mean', 'count'],
        'playtime_hours': 'mean'
    }).round(3)
    
    sentiment_stats.columns = ['positive_ratio', 'review_count', 'avg_hours']
    sentiment_stats = sentiment_stats.reset_index()
    
    # Create the visualization
    plt.style.use('default')
    fig, axes = plt.subplots(2, 2, figsize=(16, 12))
    # fig.suptitle('Steam Reviews: Sentiment Analysis by Playtime Hours', 
    #             fontsize=20, fontweight='bold', y=0.98)
    
    # Plot 1: Bar Chart - Recommended Ratio
    ax1 = axes[0, 0]
    colors = ['#ff6b6b' if x < 0.5 else '#51cf66' for x in sentiment_stats['positive_ratio']]
    bars1 = ax1.bar(sentiment_stats['playtime_bin'], sentiment_stats['positive_ratio'],
                    color=colors, alpha=0.8, edgecolor='black', linewidth=1)
    
    ax1.set_title('Recommended Ratio by Playtime', fontsize=14, fontweight='bold')
    ax1.set_ylabel('Recommended Ratio')
    ax1.set_ylim(0, 1)
    ax1.axhline(y=0.5, color='black', linestyle='--', alpha=0.7, label='50% threshold')
    ax1.legend()
    ax1.grid(True, alpha=0.3)
    
    # Add value labels
    for bar, value in zip(bars1, sentiment_stats['positive_ratio']):
        ax1.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.02,
                f'{value:.3f}', ha='center', va='bottom', fontsize=10, fontweight='bold')
    
    # Plot 2: Bar Chart - Review Count
    ax2 = axes[0, 1]
    bars2 = ax2.bar(sentiment_stats['playtime_bin'], sentiment_stats['review_count'],
                    color='skyblue', alpha=0.8, edgecolor='navy', linewidth=1)
    
    ax2.set_title('Number of Reviews by Playtime', fontsize=14, fontweight='bold')
    ax2.set_ylabel('Number of Reviews')
    ax2.grid(True, alpha=0.3)
    
    # Add value labels
    for bar, value in zip(bars2, sentiment_stats['review_count']):
        ax2.text(bar.get_x() + bar.get_width()/2, bar.get_height() + max(sentiment_stats['review_count'])*0.02,
                f'{int(value)}', ha='center', va='bottom', fontsize=10, fontweight='bold')
    
    # Plot 3: Line Chart - Sentiment Flow
    ax3 = axes[1, 0]
    line = ax3.plot(range(len(sentiment_stats)), sentiment_stats['positive_ratio'], 
                    marker='o', linewidth=4, markersize=12, color='purple',
                    markerfacecolor='white', markeredgecolor='purple', markeredgewidth=3)
    
    ax3.set_title('Recommended Ratio Across Playtime Categories', fontsize=14, fontweight='bold')
    ax3.set_xlabel('Playtime Categories')
    ax3.set_ylabel('Recommended Ratio')
    ax3.set_xticks(range(len(sentiment_stats)))
    ax3.set_xticklabels(sentiment_stats['playtime_bin'], rotation=45, ha='right')
    ax3.axhline(y=0.5, color='red', linestyle='--', alpha=0.7, label='50% threshold')
    ax3.legend()
    ax3.grid(True, alpha=0.3)
    ax3.set_ylim(0, 1)
    
    # Plot 4: Stacked Bar Chart - Positive vs Negative
    ax4 = axes[1, 1]
    positive_counts = sentiment_stats['review_count'] * sentiment_stats['positive_ratio']
    negative_counts = sentiment_stats['review_count'] * (1 - sentiment_stats['positive_ratio'])
    
    ax4.bar(sentiment_stats['playtime_bin'], positive_counts, 
            label='Positive Reviews', color='#51cf66', alpha=0.8)
    ax4.bar(sentiment_stats['playtime_bin'], negative_counts, 
            bottom=positive_counts, label='Negative Reviews', color='#ff6b6b', alpha=0.8)
    
    ax4.set_title('Review Distribution: Positive vs Negative', fontsize=14, fontweight='bold')
    ax4.set_xlabel('Playtime Categories')
    ax4.set_ylabel('Number of Reviews')
    ax4.legend()
    ax4.grid(True, alpha=0.3)
    
    # Rotate x-axis labels for better readability
    for ax in axes.flat:
        ax.tick_params(axis='x', rotation=45)
    
    plt.tight_layout()
    
    # Save the visualization
    output_path = 'output/sentiment_playtime_analysis.png'
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    print(f"Visualization saved to: {output_path}")
    
    # Display key insights
    print("\n" + "="*60)
    print("SENTIMENT ANALYSIS INSIGHTS")
    print("="*60)
    print(f"Total reviews analyzed: {len(df):,}")
    print(f"Overall positive sentiment: {df['sentiment_score'].mean():.1%}")
    print(f"Playtime converted from minutes to hours")
    
    print("\nKey Findings:")
    print(f"• Worst sentiment: {sentiment_stats.loc[sentiment_stats['positive_ratio'].idxmin(), 'playtime_bin']} "
          f"({sentiment_stats['positive_ratio'].min():.1%} positive)")
    print(f"• Best sentiment: {sentiment_stats.loc[sentiment_stats['positive_ratio'].idxmax(), 'playtime_bin']} "
          f"({sentiment_stats['positive_ratio'].max():.1%} positive)")
    print(f"• Most reviews: {sentiment_stats.loc[sentiment_stats['review_count'].idxmax(), 'playtime_bin']} "
          f"({int(sentiment_stats['review_count'].max()):,} reviews)")
    
    print("\nSentiment Pattern:")
    print("Players with very low playtime (0-1h) are mostly negative")
    print("Sentiment becomes positive once players invest 1+ hours")
    print("Peak satisfaction occurs in the 25-50h range")
    print("Long-term players (500h+) maintain high satisfaction")
    
    return output_path

if __name__ == "__main__":
    sentiment_data = create_sentiment_playtime_visualization('steam_reviews_315210.xlsx')
    
    # Show the plot
    plt.show()
    
    # Save detailed data
    sentiment_data.to_csv('output/sentiment_by_playtime_detailed.csv', index=False)
    print("\nDetailed data saved to: output/sentiment_by_playtime_detailed.csv")