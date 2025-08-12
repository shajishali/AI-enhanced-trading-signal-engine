#!/usr/bin/env python3
"""
Simple test script for AI Trading Engine
Run this to test all functionality with Playwright
"""

import asyncio
import sys
import os

# Add tests directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'tests'))

async def run_basic_tests():
    """Run basic functionality tests"""
    try:
        from test_ai_trading_engine import TestAITradingEngine
        
        print("🚀 Starting AI Trading Engine Tests...")
        print("=" * 50)
        
        # Create test instance
        test_suite = TestAITradingEngine()
        
        # Run tests
        await test_suite.run_all_tests()
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("Make sure you have installed testing dependencies:")
        print("pip install -r requirements-testing.txt")
    except Exception as e:
        print(f"❌ Test error: {e}")

def check_dependencies():
    """Check if required dependencies are installed"""
    try:
        import playwright
        print("✅ Playwright is installed")
        return True
    except ImportError:
        print("❌ Playwright is not installed")
        print("Install with: pip install playwright")
        return False

def check_server():
    """Check if Django server is running"""
    try:
        import requests
        response = requests.get("http://127.0.0.1:8000/", timeout=5)
        if response.status_code == 200:
            print("✅ Django server is running")
            return True
        else:
            print(f"⚠️ Django server status: {response.status_code}")
            return False
    except Exception as e:
        print("❌ Django server is not accessible")
        print("Start with: python manage.py runserver")
        return False

async def main():
    """Main function"""
    print("🔍 Checking prerequisites...")
    
    if not check_dependencies():
        return
    
    if not check_server():
        return
    
    print("\n✅ All prerequisites met. Starting tests...")
    await run_basic_tests()

if __name__ == "__main__":
    asyncio.run(main())
