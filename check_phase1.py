#!/usr/bin/env python3
"""
Phase 1 Status Check Script
"""

import os
import sys
import django
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ai_trading_engine.settings')
django.setup()

from django.db import connection
from django.core.management import execute_from_command_line
from apps.data.models import DataSource, MarketData, TechnicalIndicator, Symbol, DataSyncLog
from apps.data.services import CoinGeckoService, CryptoDataIngestionService, TechnicalAnalysisService

def check_database():
    """Check database connectivity and models"""
    print("🔍 Checking database...")
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
        print("✅ Database connection: OK")
        return True
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        return False

def check_models():
    """Check if models can be accessed"""
    print("\n🔍 Checking models...")
    try:
        # Check if we can query models
        symbol_count = Symbol.objects.count()
        data_source_count = DataSource.objects.count()
        market_data_count = MarketData.objects.count()
        indicator_count = TechnicalIndicator.objects.count()
        sync_log_count = DataSyncLog.objects.count()
        
        print(f"✅ Models accessible:")
        print(f"   - Symbols: {symbol_count}")
        print(f"   - Data Sources: {data_source_count}")
        print(f"   - Market Data: {market_data_count}")
        print(f"   - Technical Indicators: {indicator_count}")
        print(f"   - Sync Logs: {sync_log_count}")
        return True
    except Exception as e:
        print(f"❌ Model access failed: {e}")
        return False

def check_services():
    """Check if services can be instantiated"""
    print("\n🔍 Checking services...")
    try:
        # Test service instantiation
        coingecko_service = CoinGeckoService()
        data_service = CryptoDataIngestionService()
        analysis_service = TechnicalAnalysisService()
        
        print("✅ Services instantiated successfully:")
        print("   - CoinGeckoService: OK")
        print("   - CryptoDataIngestionService: OK")
        print("   - TechnicalAnalysisService: OK")
        return True
    except Exception as e:
        print(f"❌ Service instantiation failed: {e}")
        return False

def check_api_connectivity():
    """Check CoinGecko API connectivity"""
    print("\n🔍 Checking API connectivity...")
    try:
        service = CoinGeckoService()
        coins = service.get_top_coins(limit=5)
        
        if coins:
            print(f"✅ CoinGecko API: OK ({len(coins)} coins retrieved)")
            for coin in coins[:3]:
                print(f"   - {coin['symbol'].upper()}: {coin['name']}")
            return True
        else:
            print("⚠️  CoinGecko API: No data returned")
            return False
    except Exception as e:
        print(f"❌ CoinGecko API failed: {e}")
        return False

def check_urls():
    """Check if URLs are properly configured"""
    print("\n🔍 Checking URL configuration...")
    try:
        from django.urls import reverse
        from django.test import Client
        
        client = Client()
        
        # Test dashboard URL
        dashboard_url = reverse('data:dashboard')
        print(f"✅ Dashboard URL: {dashboard_url}")
        
        # Test API URLs
        market_data_url = reverse('data:market_data', args=[1])
        indicators_url = reverse('data:technical_indicators', args=[1])
        sync_url = reverse('data:sync_data')
        calculate_url = reverse('data:calculate_indicators')
        
        print(f"✅ API URLs configured:")
        print(f"   - Market Data: {market_data_url}")
        print(f"   - Indicators: {indicators_url}")
        print(f"   - Sync: {sync_url}")
        print(f"   - Calculate: {calculate_url}")
        
        return True
    except Exception as e:
        print(f"❌ URL configuration failed: {e}")
        return False

def check_management_commands():
    """Check if management commands are available"""
    print("\n🔍 Checking management commands...")
    try:
        from django.core.management import get_commands
        commands = get_commands()
        
        if 'sync_crypto_data' in commands:
            print("✅ Management command available: sync_crypto_data")
            return True
        else:
            print("❌ Management command not found: sync_crypto_data")
            return False
    except Exception as e:
        print(f"❌ Management command check failed: {e}")
        return False

def check_templates():
    """Check if templates exist"""
    print("\n🔍 Checking templates...")
    try:
        template_path = Path("templates/data/dashboard.html")
        if template_path.exists():
            print("✅ Dashboard template: OK")
            return True
        else:
            print("❌ Dashboard template not found")
            return False
    except Exception as e:
        print(f"❌ Template check failed: {e}")
        return False

def run_tests():
    """Run the test suite"""
    print("\n🧪 Running tests...")
    try:
        # Run tests silently
        result = execute_from_command_line(['manage.py', 'test', 'apps.data.tests', '--verbosity=0'])
        print("✅ Tests completed")
        return True
    except Exception as e:
        print(f"❌ Tests failed: {e}")
        return False

def main():
    """Run all checks"""
    print("🚀 Phase 1 Status Check")
    print("=" * 50)
    
    checks = [
        ("Database", check_database),
        ("Models", check_models),
        ("Services", check_services),
        ("API Connectivity", check_api_connectivity),
        ("URLs", check_urls),
        ("Management Commands", check_management_commands),
        ("Templates", check_templates),
        ("Tests", run_tests),
    ]
    
    results = []
    for name, check_func in checks:
        try:
            result = check_func()
            results.append((name, result))
        except Exception as e:
            print(f"❌ {name} check failed with exception: {e}")
            results.append((name, False))
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 CHECK SUMMARY")
    print("=" * 50)
    
    passed = 0
    total = len(results)
    
    for name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{name:20} {status}")
        if result:
            passed += 1
    
    print("=" * 50)
    print(f"Overall: {passed}/{total} checks passed")
    
    if passed == total:
        print("🎉 Phase 1 is ready to run!")
        print("\n📋 Next steps:")
        print("1. Start the server: python manage.py runserver")
        print("2. Visit dashboard: http://localhost:8000/data/dashboard/")
        print("3. Sync data: python manage.py sync_crypto_data")
    else:
        print("⚠️  Some checks failed. Please review the errors above.")
        print("\n🔧 Troubleshooting:")
        print("1. Run migrations: python manage.py migrate")
        print("2. Install requirements: pip install -r requirements.txt")
        print("3. Check database connection")
        print("4. Verify API keys and connectivity")

if __name__ == "__main__":
    main()




