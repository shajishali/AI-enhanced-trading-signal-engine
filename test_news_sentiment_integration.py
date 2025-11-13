"""
Test script for Phase 5: News and Sentiment Integration
This script manually tests news and sentiment data collection as specified in fixAutomate.md Phase 5, Step 5.3
"""
import os
import sys
import django

# Setup Django environment
sys.path.insert(0, os.path.dirname(__file__))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ai_trading_engine.settings')
django.setup()

from django.utils import timezone
from datetime import timedelta
from apps.sentiment.tasks import collect_news_data, aggregate_sentiment_scores
from apps.sentiment.models import NewsArticle, CryptoMention, SentimentAggregate

def test_news_collection():
    """Test news data collection"""
    print("=" * 60)
    print("Testing News Data Collection")
    print("=" * 60)
    
    # Count news articles before
    news_before = NewsArticle.objects.count()
    mentions_before = CryptoMention.objects.filter(mention_type='news').count()
    
    print(f"News articles before: {news_before}")
    print(f"News mentions before: {mentions_before}")
    
    try:
        # Run news collection task
        print("\nRunning collect_news_data() task...")
        result = collect_news_data()
        print(f"Task completed: {result}")
        
        # Count news articles after
        news_after = NewsArticle.objects.count()
        mentions_after = CryptoMention.objects.filter(mention_type='news').count()
        
        print(f"\nNews articles after: {news_after}")
        print(f"News mentions after: {mentions_after}")
        print(f"New articles collected: {news_after - news_before}")
        print(f"New mentions created: {mentions_after - mentions_before}")
        
        # Check recent news (last 24 hours)
        recent_news = NewsArticle.objects.filter(
            published_at__gte=timezone.now() - timedelta(hours=24)
        ).count()
        print(f"\nRecent news articles (last 24h): {recent_news}")
        
        # Show sample recent news
        if recent_news > 0:
            print("\nSample recent news articles:")
            sample_news = NewsArticle.objects.filter(
                published_at__gte=timezone.now() - timedelta(hours=24)
            ).order_by('-published_at')[:5]
            
            for article in sample_news:
                print(f"  - {article.title[:60]}...")
                print(f"    Source: {article.source.name}")
                print(f"    Sentiment: {article.sentiment_label} ({article.sentiment_score:.2f})")
                print(f"    Published: {article.published_at}")
                print()
        
        return True
        
    except Exception as e:
        print(f"\nERROR: News collection failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_sentiment_aggregation():
    """Test sentiment aggregation"""
    print("=" * 60)
    print("Testing Sentiment Aggregation")
    print("=" * 60)
    
    # Count sentiment aggregates before
    aggregates_before = SentimentAggregate.objects.count()
    
    print(f"Sentiment aggregates before: {aggregates_before}")
    
    try:
        # Run sentiment aggregation task
        print("\nRunning aggregate_sentiment_scores() task...")
        result = aggregate_sentiment_scores()
        print(f"Task completed: {result}")
        
        # Count sentiment aggregates after
        aggregates_after = SentimentAggregate.objects.count()
        
        print(f"\nSentiment aggregates after: {aggregates_after}")
        print(f"New aggregates created: {aggregates_after - aggregates_before}")
        
        # Check recent sentiment aggregates (last 24 hours)
        recent_aggregates = SentimentAggregate.objects.filter(
            created_at__gte=timezone.now() - timedelta(hours=24)
        ).count()
        print(f"\nRecent sentiment aggregates (last 24h): {recent_aggregates}")
        
        # Show sample recent aggregates
        if recent_aggregates > 0:
            print("\nSample recent sentiment aggregates:")
            sample_aggregates = SentimentAggregate.objects.filter(
                created_at__gte=timezone.now() - timedelta(hours=24)
            ).order_by('-created_at')[:10]
            
            for agg in sample_aggregates:
                print(f"  - {agg.asset.symbol} ({agg.timeframe}):")
                print(f"    Combined Sentiment: {agg.combined_sentiment_score:.3f}")
                print(f"    Social Sentiment: {agg.social_sentiment_score:.3f}")
                print(f"    News Sentiment: {agg.news_sentiment_score:.3f}")
                print(f"    Total Mentions: {agg.total_mentions}")
                print(f"    Confidence: {agg.confidence_score:.2f}")
                print()
        
        return True
        
    except Exception as e:
        print(f"\nERROR: Sentiment aggregation failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def check_recent_data():
    """Check recent news and sentiment data"""
    print("=" * 60)
    print("Checking Recent News and Sentiment Data")
    print("=" * 60)
    
    # Check recent news
    recent_news = NewsArticle.objects.filter(
        published_at__gte=timezone.now() - timedelta(hours=24)
    ).count()
    print(f"Recent news articles (last 24h): {recent_news}")
    
    # Check recent mentions
    recent_mentions = CryptoMention.objects.filter(
        created_at__gte=timezone.now() - timedelta(hours=24)
    ).count()
    print(f"Recent crypto mentions (last 24h): {recent_mentions}")
    
    # Check recent sentiment aggregates
    recent_aggregates = SentimentAggregate.objects.filter(
        created_at__gte=timezone.now() - timedelta(hours=24)
    ).count()
    print(f"Recent sentiment aggregates (last 24h): {recent_aggregates}")
    
    # Check news mentions by type
    news_mentions = CryptoMention.objects.filter(
        mention_type='news',
        created_at__gte=timezone.now() - timedelta(hours=24)
    ).count()
    print(f"News mentions (last 24h): {news_mentions}")
    
    # Check social mentions
    social_mentions = CryptoMention.objects.filter(
        mention_type='social',
        created_at__gte=timezone.now() - timedelta(hours=24)
    ).count()
    print(f"Social mentions (last 24h): {social_mentions}")
    
    print("\n" + "=" * 60)
    if recent_news > 0 and recent_aggregates > 0:
        print("✓ News and sentiment data collection is working")
    else:
        print("⚠ Warning: Limited or no recent data found")
        print("  This may be normal if:")
        print("  - Tasks haven't run yet")
        print("  - News API key is not configured")
        print("  - No recent news/articles available")
    print("=" * 60)


def main():
    """Main test function"""
    print("\n" + "=" * 60)
    print("Phase 5: News and Sentiment Integration Test")
    print("=" * 60)
    print()
    
    # Step 1: Test news collection
    news_success = test_news_collection()
    print()
    
    # Step 2: Test sentiment aggregation
    sentiment_success = test_sentiment_aggregation()
    print()
    
    # Step 3: Check recent data
    check_recent_data()
    print()
    
    # Summary
    print("=" * 60)
    print("Test Summary")
    print("=" * 60)
    print(f"News Collection: {'✓ PASSED' if news_success else '✗ FAILED'}")
    print(f"Sentiment Aggregation: {'✓ PASSED' if sentiment_success else '✗ FAILED'}")
    print()
    
    if news_success and sentiment_success:
        print("✓ All tests passed! News and sentiment integration is working.")
    else:
        print("✗ Some tests failed. Check the error messages above.")
    print("=" * 60)


if __name__ == "__main__":
    main()









