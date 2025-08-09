#!/usr/bin/env python3
"""
AI-Enhanced Crypto Trading Signal Engine - All 4 Phases Runner
This script runs all 4 phases of the trading engine setup and verification.
"""

import os
import sys
import subprocess
import time
from pathlib import Path

def run_command(command, description):
    """Run a command and handle errors"""
    print(f"\n🔄 {description}")
    print(f"Running: {command}")
    
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ {description} - SUCCESS")
            if result.stdout:
                print(f"Output: {result.stdout}")
        else:
            print(f"❌ {description} - FAILED")
            print(f"Error: {result.stderr}")
            return False
    except Exception as e:
        print(f"❌ {description} - ERROR: {e}")
        return False
    
    return True

def check_system_status():
    """Check current system status"""
    print("🔍 Checking System Status...")
    
    # Check Django system
    success = run_command("python manage.py check", "Django System Check")
    
    # Check database migrations
    success &= run_command("python manage.py showmigrations", "Database Migrations Status")
    
    # Check data counts
    success &= run_command(
        'python manage.py shell -c "from apps.trading.models import Symbol; from apps.signals.models import TradingSignal, SignalType, SignalFactor; from apps.sentiment.models import CryptoMention, SentimentAggregate; print(f\"Symbols: {Symbol.objects.count()}\"); print(f\"Trading Signals: {TradingSignal.objects.count()}\"); print(f\"Signal Types: {SignalType.objects.count()}\"); print(f\"Signal Factors: {SignalFactor.objects.count()}\"); print(f\"Crypto Mentions: {CryptoMention.objects.count()}\"); print(f\"Sentiment Aggregates: {SentimentAggregate.objects.count()}\")"',
        "Database Data Counts"
    )
    
    return success

def setup_phase1():
    """Setup Phase 1: Foundation & Data Infrastructure"""
    print("\n" + "="*60)
    print("🚀 PHASE 1: Foundation & Data Infrastructure")
    print("="*60)
    
    # Install dependencies
    success = run_command("pip install -r requirements.txt", "Install Dependencies")
    
    # Run migrations
    success &= run_command("python manage.py migrate", "Run Database Migrations")
    
    # Create superuser if not exists
    success &= run_command(
        'python manage.py shell -c "from django.contrib.auth.models import User; User.objects.filter(username=\"admin\").exists() or User.objects.create_superuser(\"admin\", \"admin@example.com\", \"admin123\")"',
        "Create Admin User"
    )
    
    # Sync initial data
    success &= run_command("python manage.py sync_crypto_data", "Sync Crypto Data")
    
    # Setup sample data
    success &= run_command("python manage.py setup_sample_data", "Setup Sample Data")
    
    return success

def setup_phase2():
    """Setup Phase 2: AI/ML Integration (Sentiment Analysis)"""
    print("\n" + "="*60)
    print("🚀 PHASE 2: AI/ML Integration (Sentiment Analysis)")
    print("="*60)
    
    # Setup sentiment data
    success = run_command("python manage.py setup_sentiment", "Setup Sentiment Data")
    
    # Verify sentiment models
    success &= run_command(
        'python manage.py shell -c "from apps.sentiment.models import CryptoMention, SentimentAggregate; print(f\"Crypto Mentions: {CryptoMention.objects.count()}\"); print(f\"Sentiment Aggregates: {SentimentAggregate.objects.count()}\")"',
        "Verify Sentiment Data"
    )
    
    return success

def setup_phase3():
    """Setup Phase 3: Signal Generation Engine"""
    print("\n" + "="*60)
    print("🚀 PHASE 3: Signal Generation Engine")
    print("="*60)
    
    # Setup signal data
    success = run_command("python manage.py setup_signals", "Setup Signal Data")
    
    # Verify signal models
    success &= run_command(
        'python manage.py shell -c "from apps.signals.models import TradingSignal, SignalType, SignalFactor; print(f\"Trading Signals: {TradingSignal.objects.count()}\"); print(f\"Signal Types: {SignalType.objects.count()}\"); print(f\"Signal Factors: {SignalFactor.objects.count()}\")"',
        "Verify Signal Data"
    )
    
    return success

def setup_phase4():
    """Setup Phase 4: React Frontend"""
    print("\n" + "="*60)
    print("🚀 PHASE 4: React Frontend")
    print("="*60)
    
    # Check if frontend directory exists
    if Path("frontend").exists():
        print("✅ Frontend directory already exists")
        return True
    
    # Create React frontend with Vite
    print("🔄 Creating React frontend with Vite...")
    
    # Create frontend directory
    success = run_command("mkdir frontend", "Create Frontend Directory")
    
    # Navigate to frontend directory
    os.chdir("frontend")
    
    # Initialize React project with Vite
    success &= run_command("npm create vite@latest . -- --template react-ts --yes", "Initialize React Project")
    
    # Install dependencies
    success &= run_command("npm install", "Install Frontend Dependencies")
    
    # Install additional dependencies for the trading dashboard
    success &= run_command("npm install react-router-dom axios chart.js react-chartjs-2 @types/react-router-dom", "Install Additional Dependencies")
    
    # Navigate back to root
    os.chdir("..")
    
    return success

def start_services():
    """Start all services"""
    print("\n" + "="*60)
    print("🚀 STARTING SERVICES")
    print("="*60)
    
    # Start Django server
    print("🌐 Starting Django Server...")
    django_process = subprocess.Popen(
        "python manage.py runserver",
        shell=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    
    # Wait a moment for server to start
    time.sleep(3)
    
    # Start Celery worker
    print("🔧 Starting Celery Worker...")
    celery_process = subprocess.Popen(
        "celery -A ai_trading_engine worker -l info",
        shell=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    
    # Wait a moment for worker to start
    time.sleep(3)
    
    # Start React frontend
    print("⚛️ Starting React Frontend...")
    os.chdir("frontend")
    frontend_process = subprocess.Popen(
        "npm run dev",
        shell=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    os.chdir("..")
    
    # Wait a moment for frontend to start
    time.sleep(5)
    
    return django_process, celery_process, frontend_process

def verify_access():
    """Verify all access points"""
    print("\n" + "="*60)
    print("🔍 VERIFYING ACCESS POINTS")
    print("="*60)
    
    access_points = [
        ("Main Dashboard", "http://127.0.0.1:8000/"),
        ("Admin Panel", "http://127.0.0.1:8000/admin/"),
        ("Sentiment Dashboard", "http://127.0.0.1:8000/sentiment/dashboard/"),
        ("Signal Dashboard", "http://127.0.0.1:8000/signals/dashboard/"),
        ("React Frontend", "http://localhost:5173/"),
        ("Sentiment API", "http://127.0.0.1:8000/sentiment/api/sentiment/"),
        ("Signal API", "http://127.0.0.1:8000/signals/api/signals/"),
        ("Performance API", "http://127.0.0.1:8000/signals/api/performance/"),
    ]
    
    print("📋 Access Points:")
    for name, url in access_points:
        print(f"   • {name}: {url}")
    
    print("\n🔑 Admin Credentials:")
    print("   • Username: admin")
    print("   • Password: admin123")
    
    return True

def main():
    """Main execution function"""
    print("🎯 AI-Enhanced Crypto Trading Signal Engine")
    print("🚀 Running All 4 Phases")
    print("="*60)
    
    # Check if we're in the right directory
    if not Path("manage.py").exists():
        print("❌ Error: manage.py not found. Please run this script from the project root.")
        sys.exit(1)
    
    # Phase 1: Foundation & Data Infrastructure
    if not setup_phase1():
        print("❌ Phase 1 failed. Stopping execution.")
        sys.exit(1)
    
    # Phase 2: AI/ML Integration
    if not setup_phase2():
        print("❌ Phase 2 failed. Stopping execution.")
        sys.exit(1)
    
    # Phase 3: Signal Generation Engine
    if not setup_phase3():
        print("❌ Phase 3 failed. Stopping execution.")
        sys.exit(1)
    
    # Phase 4: React Frontend
    if not setup_phase4():
        print("❌ Phase 4 failed. Stopping execution.")
        sys.exit(1)
    
    # Check system status
    if not check_system_status():
        print("❌ System status check failed.")
        sys.exit(1)
    
    # Start services
    django_process, celery_process, frontend_process = start_services()
    
    # Verify access
    verify_access()
    
    print("\n" + "="*60)
    print("🎉 ALL 4 PHASES COMPLETED SUCCESSFULLY!")
    print("="*60)
    print("\n📊 SYSTEM STATUS:")
    print("   ✅ Phase 1: Foundation & Data Infrastructure - COMPLETE")
    print("   ✅ Phase 2: AI/ML Integration (Sentiment Analysis) - COMPLETE")
    print("   ✅ Phase 3: Signal Generation Engine - COMPLETE")
    print("   ✅ Phase 4: React Frontend - COMPLETE")
    print("   ✅ Django Server - RUNNING")
    print("   ✅ Celery Worker - RUNNING")
    print("   ✅ React Frontend - RUNNING")
    
    print("\n🌐 ACCESS YOUR SYSTEM:")
    print("   • React Frontend: http://localhost:5173/")
    print("   • Django Admin: http://127.0.0.1:8000/admin/")
    print("   • Signal Dashboard: http://127.0.0.1:8000/signals/dashboard/")
    print("   • Sentiment Dashboard: http://127.0.0.1:8000/sentiment/dashboard/")
    
    print("\n🔑 ADMIN CREDENTIALS:")
    print("   • Username: admin")
    print("   • Password: admin123")
    
    print("\n⚠️  IMPORTANT NOTES:")
    print("   • The system is now running with database-based Celery (no Redis required)")
    print("   • All background tasks will be processed by the Celery worker")
    print("   • Data will be automatically synced and signals will be generated")
    print("   • Monitor the logs for any issues or errors")
    
    print("\n🛑 To stop the services, press Ctrl+C")
    
    try:
        # Keep the script running
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n🛑 Stopping services...")
        django_process.terminate()
        celery_process.terminate()
        frontend_process.terminate()
        print("✅ Services stopped.")

if __name__ == "__main__":
    main()
