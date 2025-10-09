#!/usr/bin/env python3
"""
Database Migration and Setup Script
Ensures all Phase 5 models are properly created and configured
"""

import os
import sys
import subprocess
from datetime import datetime

# Add the project directory to Python path
project_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_dir)

# Set Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ai_trading_engine.settings')

import django
django.setup()

from django.core.management import call_command
from django.db import transaction
from apps.trading.models import Symbol
from apps.data.models import MarketData, TechnicalIndicator
from apps.signals.models import TradingSignal, ChartImage, ChartPattern, EntryPoint, ChartMLModel, ChartMLPrediction, ABTest, RetrainingTask, ModelPerformanceMetrics

def print_status(message, status="INFO"):
    """Print status message with timestamp"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    status_symbols = {
        "INFO": "ℹ️",
        "SUCCESS": "✅", 
        "WARNING": "⚠️",
        "ERROR": "❌",
        "FIXING": "🔧"
    }
    print(f"[{timestamp}] {status_symbols.get(status, 'ℹ️')} {message}")

def run_migrations():
    """Run Django migrations"""
    print_status("=== RUNNING DATABASE MIGRATIONS ===", "FIXING")
    
    try:
        # Make migrations
        print_status("Creating migrations...", "INFO")
        call_command('makemigrations', verbosity=0)
        print_status("Migrations created!", "SUCCESS")
        
        # Apply migrations
        print_status("Applying migrations...", "INFO")
        call_command('migrate', verbosity=0)
        print_status("Migrations applied!", "SUCCESS")
        
        return True
        
    except Exception as e:
        print_status(f"Migration failed: {str(e)}", "ERROR")
        return False

def setup_default_data():
    """Setup default data for the system"""
    print_status("=== SETTING UP DEFAULT DATA ===", "FIXING")
    
    try:
        with transaction.atomic():
            # Ensure we have basic symbols
            default_symbols = [
                'BTCUSDT', 'ETHUSDT', 'BNBUSDT', 'ADAUSDT', 'SOLUSDT',
                'XRPUSDT', 'DOTUSDT', 'DOGEUSDT', 'AVAXUSDT', 'MATICUSDT'
            ]
            
            created_count = 0
            for symbol_code in default_symbols:
                symbol, created = Symbol.objects.get_or_create(
                    symbol=symbol_code,
                    defaults={
                        'name': symbol_code.replace('USDT', '/USDT'),
                        'is_active': True,
                        'is_crypto': True,
                        'base_currency': symbol_code.replace('USDT', ''),
                        'quote_currency': 'USDT'
                    }
                )
                if created:
                    created_count += 1
            
            print_status(f"Created {created_count} new symbols", "SUCCESS")
            
            # Activate all symbols
            Symbol.objects.update(is_active=True)
            active_count = Symbol.objects.filter(is_active=True).count()
            print_status(f"Total active symbols: {active_count}", "SUCCESS")
            
        return True
        
    except Exception as e:
        print_status(f"Setup failed: {str(e)}", "ERROR")
        return False

def create_sample_ml_model():
    """Create a sample ML model for testing"""
    print_status("=== CREATING SAMPLE ML MODEL ===", "FIXING")
    
    try:
        # Check if we already have ML models
        existing_models = ChartMLModel.objects.count()
        if existing_models > 0:
            print_status(f"Found {existing_models} existing ML models", "INFO")
            return True
        
        # Create a sample ML model
        sample_model = ChartMLModel.objects.create(
            name="Sample CNN Model",
            model_type="CNN",
            version="1.0",
            status="TRAINED",
            target_task="ENTRY_POINT_DETECTION",
            prediction_horizon="REALTIME",
            accuracy_score=0.75,
            precision_score=0.72,
            recall_score=0.78,
            f1_score=0.75,
            training_data_size=1000,
            training_parameters='{"epochs": 100, "batch_size": 32}',
            is_active=True
        )
        
        print_status(f"Created sample ML model: {sample_model.name}", "SUCCESS")
        return True
        
    except Exception as e:
        print_status(f"Failed to create sample ML model: {str(e)}", "ERROR")
        return False

def verify_database_integrity():
    """Verify database integrity"""
    print_status("=== VERIFYING DATABASE INTEGRITY ===", "FIXING")
    
    try:
        # Check all models can be accessed
        models_to_check = [
            ('Symbol', Symbol),
            ('MarketData', MarketData),
            ('TechnicalIndicator', TechnicalIndicator),
            ('TradingSignal', TradingSignal),
            ('ChartImage', ChartImage),
            ('ChartPattern', ChartPattern),
            ('EntryPoint', EntryPoint),
            ('ChartMLModel', ChartMLModel),
            ('ChartMLPrediction', ChartMLPrediction),
            ('ABTest', ABTest),
            ('RetrainingTask', RetrainingTask),
            ('ModelPerformanceMetrics', ModelPerformanceMetrics),
        ]
        
        for model_name, model_class in models_to_check:
            try:
                count = model_class.objects.count()
                print_status(f"{model_name}: {count} records", "SUCCESS")
            except Exception as e:
                print_status(f"{model_name}: Error - {str(e)}", "ERROR")
                return False
        
        return True
        
    except Exception as e:
        print_status(f"Database integrity check failed: {str(e)}", "ERROR")
        return False

def create_management_commands():
    """Create additional management commands for easier system management"""
    
    # Create a comprehensive system status command
    status_command = """from django.core.management.base import BaseCommand
from apps.trading.models import Symbol
from apps.data.models import MarketData, TechnicalIndicator
from apps.signals.models import TradingSignal, ChartMLModel
from datetime import datetime, timedelta
from django.utils import timezone

class Command(BaseCommand):
    help = 'Check system status for signal generation'

    def handle(self, *args, **options):
        print("=== SIGNAL GENERATION SYSTEM STATUS ===")
        print(f"Timestamp: {datetime.now()}")
        print()
        
        # Symbols
        total_symbols = Symbol.objects.count()
        active_symbols = Symbol.objects.filter(is_active=True).count()
        print(f"Symbols: {active_symbols}/{total_symbols} active")
        
        # Market Data
        market_data_count = MarketData.objects.count()
        latest_market_data = MarketData.objects.order_by('-timestamp').first()
        if latest_market_data:
            time_diff = datetime.now(timezone.utc) - latest_market_data.timestamp
            print(f"Market Data: {market_data_count} records, latest {time_diff.total_seconds()/60:.1f} minutes ago")
        else:
            print("Market Data: No data found!")
        
        # Technical Indicators
        indicator_count = TechnicalIndicator.objects.count()
        latest_indicator = TechnicalIndicator.objects.order_by('-timestamp').first()
        if latest_indicator:
            time_diff = datetime.now(timezone.utc) - latest_indicator.timestamp
            print(f"Technical Indicators: {indicator_count} records, latest {time_diff.total_seconds()/60:.1f} minutes ago")
        else:
            print("Technical Indicators: No data found!")
        
        # Active Signals
        active_signals = TradingSignal.objects.filter(is_valid=True).count()
        print(f"Active Signals: {active_signals}")
        
        # Recent Signals
        recent_signals = TradingSignal.objects.filter(
            created_at__gte=datetime.now(timezone.utc) - timedelta(hours=1)
        ).count()
        print(f"Signals in last hour: {recent_signals}")
        
        # ML Models
        ml_models = ChartMLModel.objects.count()
        active_ml_models = ChartMLModel.objects.filter(is_active=True).count()
        print(f"ML Models: {active_ml_models}/{ml_models} active")
        
        print()
        if active_signals > 0 or recent_signals > 0:
            print("✅ System appears to be working!")
        else:
            print("❌ System may have issues - no recent signals generated")
"""
    
    # Write the status command
    status_file = os.path.join(project_dir, 'apps', 'signals', 'management', 'commands', 'system_status.py')
    os.makedirs(os.path.dirname(status_file), exist_ok=True)
    
    with open(status_file, 'w') as f:
        f.write(status_command)
    
    print_status("Created system_status management command", "SUCCESS")

def main():
    """Main function to setup database and system"""
    print_status("=== DATABASE SETUP AND MIGRATION SCRIPT ===", "INFO")
    print_status("This script will setup the database and ensure all Phase 5 models are ready", "INFO")
    print()
    
    # Track success of each step
    steps_successful = []
    
    # Step 1: Run migrations
    steps_successful.append(run_migrations())
    
    # Step 2: Setup default data
    steps_successful.append(setup_default_data())
    
    # Step 3: Create sample ML model
    steps_successful.append(create_sample_ml_model())
    
    # Step 4: Verify database integrity
    steps_successful.append(verify_database_integrity())
    
    # Step 5: Create management commands
    create_management_commands()
    
    # Summary
    print()
    print_status("=== SETUP SUMMARY ===", "INFO")
    successful_steps = sum(steps_successful)
    total_steps = len(steps_successful)
    
    print_status(f"Completed {successful_steps}/{total_steps} steps", "SUCCESS" if successful_steps == total_steps else "WARNING")
    
    if successful_steps == total_steps:
        print_status("🎉 DATABASE SETUP COMPLETE! All Phase 5 models are ready.", "SUCCESS")
        print_status("Next steps:", "INFO")
        print_status("1. Run: python fix_signal_generation_issues.py", "INFO")
        print_status("2. Check status: python manage.py system_status", "INFO")
    else:
        print_status("⚠️ Some steps failed. Check the errors above.", "WARNING")
    
    print()
    print_status("Database setup completed!", "INFO")

if __name__ == "__main__":
    main()























