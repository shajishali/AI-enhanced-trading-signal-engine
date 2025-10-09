#!/usr/bin/env python3
"""
Test script for the News Feed API endpoint
"""

import requests
import json

def test_news_feed_api():
    """Test the news feed API endpoint"""
    
    # Base URL for the development server
    base_url = "http://localhost:8000"
    
    # Test the news feed endpoint
    print("🧪 Testing News Feed API...")
    print("=" * 50)
    
    try:
        # Test the news feed endpoint
        response = requests.get(f"{base_url}/analytics/api/news-feed/")
        
        print(f"📡 Status Code: {response.status_code}")
        print(f"🔗 URL: {base_url}/analytics/api/news-feed/")
        
        if response.status_code == 200:
            try:
                data = response.json()
                print("✅ API Response:")
                print(f"   - Success: {data.get('success', False)}")
                print(f"   - Total News: {data.get('total_count', 0)}")
                print(f"   - Category: {data.get('category', 'N/A')}")
                print(f"   - Timestamp: {data.get('timestamp', 'N/A')}")
                
                if data.get('news'):
                    print("\n📰 Sample News Articles:")
                    for i, article in enumerate(data['news'][:3]):
                        print(f"   {i+1}. {article.get('title', 'No title')[:60]}...")
                        print(f"      Sentiment: {article.get('sentiment_label', 'N/A')}")
                        print(f"      Source: {article.get('source_name', 'N/A')}")
                        print(f"      Time: {article.get('time_ago', 'N/A')}")
                        print()
                else:
                    print("⚠️  No news articles found in response")
                    
            except json.JSONDecodeError:
                print("❌ Response is not valid JSON")
                print(f"   Content: {response.text[:200]}...")
                
        elif response.status_code == 401:
            print("🔒 Authentication required - this is expected for protected endpoints")
            print("   The endpoint is working but requires user login")
            
        elif response.status_code == 404:
            print("❌ Endpoint not found - check URL routing")
            
        else:
            print(f"❌ Unexpected status code: {response.status_code}")
            print(f"   Content: {response.text[:200]}...")
            
    except requests.exceptions.ConnectionError:
        print("❌ Connection failed - make sure the Django server is running on port 8000")
        print("   Run: python manage.py runserver 0.0.0.0:8000")
        
    except Exception as e:
        print(f"❌ Error testing API: {e}")
    
    print("\n" + "=" * 50)
    print("🏁 Test completed!")

if __name__ == "__main__":
    test_news_feed_api()






























