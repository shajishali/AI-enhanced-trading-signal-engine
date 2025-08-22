#!/usr/bin/env python3
"""
Test script to check if Django can start without import errors
"""

import os
import sys
import django

def test_django_imports():
    """Test if Django can import all modules without errors"""
    try:
        # Set up Django environment
        os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ai_trading_engine.settings')
        django.setup()
        
        print("✅ Django environment setup successful!")
        
        # Test importing core modules
        from apps.core import views
        print("✅ Core views imported successfully!")
        
        from apps.core import urls
        print("✅ Core URLs imported successfully!")
        
        from apps.core.services import market_broadcaster, signals_broadcaster, notification_broadcaster
        print("✅ Broadcasting services imported successfully!")
        
        # Test URL resolution
        from django.urls import reverse
        try:
            websocket_test_url = reverse('core:websocket_test')
            print(f"✅ WebSocket test URL resolved: {websocket_test_url}")
        except Exception as e:
            print(f"⚠️ URL resolution warning: {e}")
        
        print("\n🎉 All imports successful! Django is ready to run.")
        return True
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False
        
    except Exception as e:
        print(f"❌ Django setup error: {e}")
        return False

if __name__ == "__main__":
    print("Testing Django imports...")
    success = test_django_imports()
    
    if success:
        print("\n✅ Django is ready! You can now start the server.")
        print("Run: python manage.py runserver")
        print("Or: daphne -b 127.0.0.1 -p 8000 ai_trading_engine.asgi:application")
    else:
        print("\n💥 Django setup failed. Please fix the import errors above.")
        sys.exit(1)









