#!/usr/bin/env python3
"""
Quick Diagnostic Script - Check Current Signal Generation Status
Run this to see what's working and what needs fixing
"""

import os
import sys
import subprocess
from datetime import datetime, timedelta

# Add the project directory to Python path
project_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_dir)

# Set Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ai_trading_engine.settings')

import django
django.setup()

from django.utils import timezone
from apps.trading.models import Symbol
from apps.data.models import MarketData, TechnicalIndicator
from apps.signals.models import TradingSignal, ChartMLModel

def print_status(message, status="INFO"):
    """Print status message with timestamp"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    status_symbols = {
        "INFO": "ℹ️",
        "SUCCESS": "✅", 
        "WARNING": "⚠️",
        "ERROR": "❌",
        "CHECK": "🔍"
    }
    print(f"[{timestamp}] {status_symbols.get(status, 'ℹ️')} {message}")

def check_celery_status():
    """Check if Celery is running"""
    print_status("=== CELERY STATUS ===", "CHECK")
    
    try:
        result = subprocess.run(['celery', '-A', 'ai_trading_engine', 'inspect', 'active'], 
                              capture_output=True, text=True, timeout=10)
        
        if result.returncode == 0 and result.stdout.strip():
            print_status("✅ Celery workers are running", "SUCCESS")
            return True
        else:
            print_status("❌ Celery workers are not running", "ERROR")
            return False
            
    except subprocess.TimeoutExpired:
        print_status("❌ Celery check timed out - workers likely not running", "ERROR")
        return False
    except FileNotFoundError:
        print_status("❌ Celery command not found - Celery not installed", "ERROR")
        return False
    except Exception as e:
        print_status(f"❌ Error checking Celery: {str(e)}", "ERROR")
        return False

def check_database_status():
    """Check database status"""
    print_status("=== DATABASE STATUS ===", "CHECK")
    
    try:
        # Check symbols
        total_symbols = Symbol.objects.count()
        active_symbols = Symbol.objects.filter(is_active=True).count()
        
        if active_symbols > 0:
            print_status(f"✅ Symbols: {active_symbols}/{total_symbols} active", "SUCCESS")
        else:
            print_status(f"❌ Symbols: {active_symbols}/{total_symbols} active - NO ACTIVE SYMBOLS!", "ERROR")
        
        # Check market data
        market_data_count = MarketData.objects.count()
        if market_data_count > 0:
            latest_data = MarketData.objects.order_by('-timestamp').first()
            time_diff = datetime.now(timezone.utc) - latest_data.timestamp
            minutes_ago = time_diff.total_seconds() / 60
            
            if minutes_ago < 60:  # Less than 1 hour
                print_status(f"✅ Market Data: {market_data_count} records, latest {minutes_ago:.1f} minutes ago", "SUCCESS")
            else:
                print_status(f"⚠️ Market Data: {market_data_count} records, latest {minutes_ago:.1f} minutes ago - STALE DATA!", "WARNING")
        else:
            print_status("❌ Market Data: No data found!", "ERROR")
        
        # Check technical indicators
        indicator_count = TechnicalIndicator.objects.count()
        if indicator_count > 0:
            latest_indicator = TechnicalIndicator.objects.order_by('-timestamp').first()
            time_diff = datetime.now(timezone.utc) - latest_indicator.timestamp
            minutes_ago = time_diff.total_seconds() / 60
            
            if minutes_ago < 60:  # Less than 1 hour
                print_status(f"✅ Technical Indicators: {indicator_count} records, latest {minutes_ago:.1f} minutes ago", "SUCCESS")
            else:
                print_status(f"⚠️ Technical Indicators: {indicator_count} records, latest {minutes_ago:.1f} minutes ago - STALE DATA!", "WARNING")
        else:
            print_status("❌ Technical Indicators: No data found!", "ERROR")
        
        # Check active signals
        active_signals = TradingSignal.objects.filter(is_valid=True).count()
        if active_signals > 0:
            print_status(f"✅ Active Signals: {active_signals}", "SUCCESS")
        else:
            print_status("⚠️ Active Signals: 0 - No current signals", "WARNING")
        
        # Check recent signals
        recent_signals = TradingSignal.objects.filter(
            created_at__gte=datetime.now(timezone.utc) - timedelta(hours=1)
        ).count()
        
        if recent_signals > 0:
            print_status(f"✅ Recent Signals: {recent_signals} in last hour", "SUCCESS")
        else:
            print_status("⚠️ Recent Signals: 0 in last hour - No recent generation", "WARNING")
        
        return True
        
    except Exception as e:
        print_status(f"❌ Database error: {str(e)}", "ERROR")
        return False

def check_ml_models():
    """Check ML models status"""
    print_status("=== ML MODELS STATUS ===", "CHECK")
    
    try:
        total_models = ChartMLModel.objects.count()
        active_models = ChartMLModel.objects.filter(is_active=True).count()
        
        if total_models > 0:
            print_status(f"✅ ML Models: {active_models}/{total_models} active", "SUCCESS")
        else:
            print_status("⚠️ ML Models: None created yet", "WARNING")
        
        return True
        
    except Exception as e:
        print_status(f"❌ ML Models error: {str(e)}", "ERROR")
        return False

def test_signal_generation():
    """Test manual signal generation"""
    print_status("=== TESTING SIGNAL GENERATION ===", "CHECK")
    
    try:
        from apps.signals.services import SignalGenerationService
        
        # Test with BTCUSDT
        try:
            symbol = Symbol.objects.get(symbol='BTCUSDT')
            service = SignalGenerationService()
            signals = service.generate_signals_for_symbol(symbol)
            
            if signals:
                print_status(f"✅ Test Signal Generation: Generated {len(signals)} signals for BTCUSDT", "SUCCESS")
                for signal in signals[:3]:  # Show first 3
                    print_status(f"   - {signal.signal_type.name}: Confidence {signal.confidence_score:.2f}", "INFO")
            else:
                print_status("⚠️ Test Signal Generation: No signals generated for BTCUSDT", "WARNING")
                
        except Symbol.DoesNotExist:
            print_status("❌ Test Signal Generation: BTCUSDT symbol not found", "ERROR")
        except Exception as e:
            print_status(f"❌ Test Signal Generation: Error - {str(e)}", "ERROR")
        
        return True
        
    except Exception as e:
        print_status(f"❌ Signal generation test failed: {str(e)}", "ERROR")
        return False

def check_dependencies():
    """Check critical dependencies"""
    print_status("=== DEPENDENCIES CHECK ===", "CHECK")
    
    critical_packages = [
        'django', 'celery', 'pandas', 'numpy', 'redis', 'psycopg2'
    ]
    
    missing_packages = []
    
    for package in critical_packages:
        try:
            __import__(package)
            print_status(f"✅ {package} - Installed", "SUCCESS")
        except ImportError:
            print_status(f"❌ {package} - Missing", "ERROR")
            missing_packages.append(package)
    
    if missing_packages:
        print_status(f"❌ Missing packages: {', '.join(missing_packages)}", "ERROR")
        return False
    else:
        print_status("✅ All critical dependencies installed", "SUCCESS")
        return True

def main():
    """Main diagnostic function"""
    print("=" * 80)
    print("🔍 AI TRADING ENGINE - QUICK DIAGNOSTIC")
    print("=" * 80)
    print(f"Timestamp: {datetime.now()}")
    print()
    
    # Run all checks
    checks = [
        ("Dependencies", check_dependencies),
        ("Database", check_database_status),
        ("Celery", check_celery_status),
        ("ML Models", check_ml_models),
        ("Signal Generation", test_signal_generation),
    ]
    
    results = []
    
    for check_name, check_func in checks:
        print_status(f"Running {check_name} check...", "CHECK")
        try:
            result = check_func()
            results.append(result)
        except Exception as e:
            print_status(f"❌ {check_name} check failed: {str(e)}", "ERROR")
            results.append(False)
        print()
    
    # Summary
    print_status("=== DIAGNOSTIC SUMMARY ===", "INFO")
    successful_checks = sum(results)
    total_checks = len(results)
    
    print_status(f"Checks passed: {successful_checks}/{total_checks}", 
                "SUCCESS" if successful_checks == total_checks else "WARNING")
    
    if successful_checks == total_checks:
        print()
        print_status("🎉 ALL SYSTEMS OPERATIONAL! Signal generation should be working.", "SUCCESS")
    else:
        print()
        print_status("⚠️ ISSUES DETECTED! Run the master fix script:", "WARNING")
        print_status("python MASTER_FIX_ALL_ISSUES.py", "INFO")
    
    print()
    print("=" * 80)

if __name__ == "__main__":
    main()

































































