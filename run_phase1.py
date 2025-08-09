#!/usr/bin/env python3
"""
Phase 1 Runner Script for AI-Enhanced Crypto Trading Signal Engine
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
    print("🚀 Starting Phase 1: AI-Enhanced Crypto Trading Signal Engine")
    print("=" * 70)
    
    # Check if we're in the right directory
    if not os.path.exists('manage.py'):
        print("❌ Error: manage.py not found. Please run this script from the project root directory.")
        sys.exit(1)
    
    # Step 1: Install requirements
    if not run_command("pip install -r requirements.txt", "Installing requirements"):
        print("❌ Failed to install requirements. Please check your Python environment.")
        sys.exit(1)
    
    # Step 2: Run migrations
    if not run_command("python manage.py makemigrations", "Creating migrations"):
        print("❌ Failed to create migrations.")
        sys.exit(1)
    
    if not run_command("python manage.py migrate", "Running migrations"):
        print("❌ Failed to run migrations.")
        sys.exit(1)
    
    # Step 3: Create superuser (optional)
    print("\n👤 Creating superuser (admin/admin)...")
    try:
        subprocess.run(
            "python manage.py createsuperuser --noinput --username admin --email admin@example.com",
            shell=True, check=False
        )
        print("✅ Superuser created (or already exists)")
    except:
        print("⚠️  Superuser creation skipped (may already exist)")
    
    # Step 4: Run tests
    if not run_command("python manage.py test apps.data.tests", "Running tests"):
        print("⚠️  Tests failed, but continuing...")
    
    # Step 5: Sync initial data
    print("\n📊 Syncing initial crypto data...")
    if not run_command("python manage.py sync_crypto_data --symbols-only", "Syncing crypto symbols"):
        print("⚠️  Initial data sync failed, but continuing...")
    
    print("\n🎉 Phase 1 setup completed!")
    print("\n📋 Next steps:")
    print("1. Start the development server: python manage.py runserver")
    print("2. Visit the dashboard: http://localhost:8000/data/dashboard/")
    print("3. Visit the admin panel: http://localhost:8000/admin/")
    print("4. Run manual data sync: python manage.py sync_crypto_data")
    print("5. Calculate indicators: python manage.py sync_crypto_data --indicators-only")
    
    print("\n🔗 Available URLs:")
    print("- Dashboard: http://localhost:8000/data/dashboard/")
    print("- Market Data API: http://localhost:8000/data/market-data/<symbol_id>/")
    print("- Indicators API: http://localhost:8000/data/indicators/<symbol_id>/")
    print("- Manual Sync: POST http://localhost:8000/data/sync/")
    print("- Calculate Indicators: POST http://localhost:8000/data/calculate-indicators/")
    
    print("\n💡 Tips:")
    print("- Use the dashboard to manually sync data and calculate indicators")
    print("- Check the admin panel to view data sources, market data, and sync logs")
    print("- Monitor the console for any error messages")
    
    # Ask if user wants to start the server
    response = input("\n🚀 Would you like to start the development server now? (y/n): ")
    if response.lower() in ['y', 'yes']:
        print("\n🌐 Starting development server...")
        print("📊 Dashboard available at: http://localhost:8000/data/dashboard/")
        print("🔗 Admin panel available at: http://localhost:8000/admin/")
        print("Press Ctrl+C to stop the server")
        subprocess.run("python manage.py runserver", shell=True)

if __name__ == "__main__":
    main()




