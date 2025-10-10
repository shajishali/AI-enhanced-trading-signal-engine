#!/usr/bin/env python3
"""
Fix TradingSignal created_at field

This script creates a migration to remove auto_now_add from created_at
so we can manually set the signal creation date.
"""

import os
import sys
import django
from django.core.management import call_command

# Setup Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ai_trading_engine.settings')
django.setup()

def print_status(message, status="INFO"):
    """Print status message with timestamp and emoji"""
    timestamp = datetime.now().strftime("%H:%M:%S")
    status_symbols = {
        "INFO": "ℹ️",
        "SUCCESS": "✅", 
        "WARNING": "⚠️",
        "ERROR": "❌",
        "DEBUG": "🔍"
    }
    print(f"[{timestamp}] {status_symbols.get(status, 'ℹ️')} {message}")

def fix_created_at_field():
    """Fix the created_at field to allow manual setting"""
    print_status("Fixing TradingSignal created_at field", "INFO")
    
    try:
        # Create a migration to modify the created_at field
        call_command('makemigrations', 'signals', name='fix_created_at_field')
        print_status("Migration created successfully", "SUCCESS")
        
        # Apply the migration
        call_command('migrate', 'signals')
        print_status("Migration applied successfully", "SUCCESS")
        
        return True
        
    except Exception as e:
        print_status(f"Error fixing created_at field: {e}", "ERROR")
        return False

def main():
    """Main function"""
    print_status("Fixing TradingSignal created_at field", "INFO")
    
    success = fix_created_at_field()
    
    if success:
        print_status("✅ TradingSignal created_at field fixed", "SUCCESS")
        print_status("Now signals can be saved with custom creation dates", "INFO")
    else:
        print_status("❌ Failed to fix created_at field", "ERROR")
    
    return success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)



