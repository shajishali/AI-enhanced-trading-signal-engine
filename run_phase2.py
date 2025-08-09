#!/usr/bin/env python3
"""
Phase 2 Runner Script for AI-Enhanced Crypto Trading Signal Engine
AI/ML Integration - Sentiment Analysis & Machine Learning
"""

import os
import sys
import subprocess
import time

def run_command(command, description):
    """Run a command and handle errors"""
    print(f"\n🔄 {description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} completed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed: {e}")
        print(f"Error output: {e.stderr}")
        return False

def main():
    print("🚀 Starting Phase 2: AI/ML Integration - Sentiment Analysis")
    print("=" * 70)
    
    # Check if we're in the right directory
    if not os.path.exists('manage.py'):
        print("❌ Error: manage.py not found. Please run this script from the project root directory.")
        sys.exit(1)
    
    # Step 1: Install additional requirements for AI/ML
    print("\n📦 Installing AI/ML dependencies...")
    ai_requirements = [
        "transformers>=4.30.0",
        "torch>=2.0.0",
        "scikit-learn>=1.3.0",
        "nltk>=3.8.1",
        "textblob>=0.17.1",
        "vaderSentiment>=3.3.2",
        "requests>=2.31.0",
        "pandas>=2.0.0",
        "numpy>=1.24.0"
    ]
    
    for req in ai_requirements:
        if not run_command(f"pip install {req}", f"Installing {req}"):
            print(f"⚠️  Failed to install {req}, but continuing...")
    
    # Step 2: Run migrations for sentiment app
    if not run_command("python manage.py makemigrations sentiment", "Creating sentiment migrations"):
        print("❌ Failed to create sentiment migrations.")
        sys.exit(1)
    
    if not run_command("python manage.py migrate", "Running migrations"):
        print("❌ Failed to run migrations.")
        sys.exit(1)
    
    # Step 3: Set up sentiment analysis system
    print("\n🧠 Setting up sentiment analysis system...")
    if not run_command("python manage.py setup_sentiment", "Setting up sentiment sources and influencers"):
        print("⚠️  Sentiment setup failed, but continuing...")
    
    # Step 4: Create sample sentiment data
    print("\n📊 Creating sample sentiment data...")
    if not run_command("python manage.py setup_sentiment --create-sample-data", "Creating sample sentiment data"):
        print("⚠️  Sample data creation failed, but continuing...")
    
    # Step 5: Test sentiment analysis
    print("\n🧪 Testing sentiment analysis...")
    if not run_command("python manage.py test apps.sentiment", "Running sentiment tests"):
        print("⚠️  Sentiment tests failed, but continuing...")
    
    # Step 6: Set up Celery tasks for sentiment
    print("\n⚡ Setting up background tasks...")
    print("Note: Make sure Redis is running for Celery tasks")
    
    print("\n🎉 Phase 2 setup completed!")
    print("\n📋 Next steps:")
    print("1. Start the development server: python manage.py runserver")
    print("2. Visit the sentiment dashboard: http://localhost:8000/sentiment/dashboard/")
    print("3. Start Celery worker: celery -A ai_trading_engine worker -l info")
    print("4. Start Celery beat: celery -A ai_trading_engine beat -l info")
    print("5. Configure API keys in settings for Twitter, Reddit, and News APIs")
    
    print("\n🔗 Available URLs:")
    print("- Sentiment Dashboard: http://localhost:8000/sentiment/dashboard/")
    print("- Sentiment API: http://localhost:8000/sentiment/api/sentiment-summary/")
    print("- Sentiment Health: http://localhost:8000/sentiment/api/health/")
    print("- Admin Panel: http://localhost:8000/admin/")
    
    print("\n🔧 Management Commands:")
    print("- Setup sentiment: python manage.py setup_sentiment")
    print("- Create sample data: python manage.py setup_sentiment --create-sample-data")
    print("- Trigger collection: POST http://localhost:8000/sentiment/api/trigger/collect/")
    print("- Trigger aggregation: POST http://localhost:8000/sentiment/api/trigger/aggregate/")
    
    print("\n💡 Phase 2 Features:")
    print("✅ Social Media Data Integration (Twitter, Reddit)")
    print("✅ News Analysis Engine")
    print("✅ Sentiment Analysis Models (Rule-based)")
    print("✅ Sentiment Aggregation System")
    print("✅ Real-time Dashboard")
    print("✅ Background Task Processing")
    print("✅ API Endpoints for Data Access")
    print("✅ Health Monitoring System")
    
    print("\n🚀 Next Phase (Phase 3): Signal Generation Engine")
    print("- Multi-factor signal generation")
    print("- AI model integration")
    print("- Advanced analytics")
    print("- Real-time signal processing")
    
    # Ask if user wants to start the server
    response = input("\n🚀 Would you like to start the development server now? (y/n): ")
    if response.lower() in ['y', 'yes']:
        print("\n🌐 Starting development server...")
        print("📊 Sentiment Dashboard available at: http://localhost:8000/sentiment/dashboard/")
        print("🔗 Admin panel available at: http://localhost:8000/admin/")
        print("Press Ctrl+C to stop the server")
        subprocess.run("python manage.py runserver", shell=True)

if __name__ == "__main__":
    main()
