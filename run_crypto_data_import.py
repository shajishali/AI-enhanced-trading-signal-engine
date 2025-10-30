#!/usr/bin/env python3
"""
Main Execution Script
Runs the complete process: cleanup -> fetch -> verify
"""

import subprocess
import sys
import time

def run_script(script_name, description):
    """Run a Python script and handle errors"""
    print(f"\n{'='*60}")
    print(f"🔄 {description}")
    print(f"{'='*60}")
    
    try:
        result = subprocess.run([sys.executable, script_name], 
                              capture_output=True, text=True, timeout=3600)
        
        if result.returncode == 0:
            print(f"✅ {description} completed successfully")
            if result.stdout:
                print("Output:")
                print(result.stdout)
        else:
            print(f"❌ {description} failed")
            if result.stderr:
                print("Error:")
                print(result.stderr)
            return False
            
    except subprocess.TimeoutExpired:
        print(f"⏰ {description} timed out after 1 hour")
        return False
    except Exception as e:
        print(f"❌ Error running {description}: {e}")
        return False
    
    return True

def main():
    """Main execution function"""
    print("🚀 CRYPTO DATA IMPORT PROCESS")
    print("This will:")
    print("1. Clean up incorrect existing data")
    print("2. Fetch fresh daily OHLC data from Binance API")
    print("3. Verify the imported data")
    
    confirm = input("\nProceed? (yes/no): ")
    if confirm.lower() != 'yes':
        print("Process cancelled")
        return
    
    # Step 1: Cleanup
    if not run_script("cleanup_incorrect_data.py", "Database Cleanup"):
        print("❌ Cleanup failed. Stopping process.")
        return
    
    print("\n⏳ Waiting 5 seconds before data fetch...")
    time.sleep(5)
    
    # Step 2: Fetch Data
    print("\n⚠️  Data fetch will take a long time (potentially hours)")
    print("This is normal due to API rate limits and large data volume")
    
    confirm_fetch = input("Continue with data fetch? (yes/no): ")
    if confirm_fetch.lower() != 'yes':
        print("Data fetch cancelled")
        return
    
    if not run_script("fetch_daily_crypto_data.py", "Data Fetch"):
        print("❌ Data fetch failed")
        return
    
    print("\n⏳ Waiting 5 seconds before verification...")
    time.sleep(5)
    
    # Step 3: Verify
    if not run_script("verify_crypto_data.py", "Data Verification"):
        print("❌ Verification failed")
        return
    
    print(f"\n{'='*60}")
    print("🎉 PROCESS COMPLETED SUCCESSFULLY!")
    print("Your database now contains accurate daily OHLC data")
    print("for all USDT pairs from 2020 to October 14, 2025")
    print(f"{'='*60}")

if __name__ == "__main__":
    main()































