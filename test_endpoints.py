#!/usr/bin/env python3
"""
Test script to verify all endpoints are working
"""

import requests
import json

BASE_URL = "http://127.0.0.1:8000"

def test_endpoint(url, name):
    """Test an endpoint and return the result"""
    try:
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            print(f"✅ {name}: {url} - SUCCESS")
            return True
        else:
            print(f"❌ {name}: {url} - FAILED (Status: {response.status_code})")
            return False
    except Exception as e:
        print(f"❌ {name}: {url} - ERROR: {e}")
        return False

def main():
    """Test all endpoints"""
    print("🔍 Testing All Endpoints...")
    print("="*50)
    
    endpoints = [
        (f"{BASE_URL}/", "Main Dashboard"),
        (f"{BASE_URL}/admin/", "Admin Panel"),
        (f"{BASE_URL}/sentiment/dashboard/", "Sentiment Dashboard"),
        (f"{BASE_URL}/signals/dashboard/", "Signal Dashboard"),
        (f"{BASE_URL}/sentiment/api/sentiment/BTC/", "Sentiment API"),
        (f"{BASE_URL}/signals/api/signals/", "Signal API"),
        (f"{BASE_URL}/signals/api/performance/", "Performance API"),
        (f"{BASE_URL}/signals/api/regimes/", "Market Regime API"),
        (f"{BASE_URL}/trading/api/symbols/", "Symbols API"),
    ]
    
    success_count = 0
    total_count = len(endpoints)
    
    for url, name in endpoints:
        if test_endpoint(url, name):
            success_count += 1
    
    print("="*50)
    print(f"📊 Results: {success_count}/{total_count} endpoints working")
    
    if success_count == total_count:
        print("🎉 All endpoints are working!")
    else:
        print("⚠️  Some endpoints need attention.")
    
    print("\n🔗 Access Links:")
    print(f"   • Main Dashboard: {BASE_URL}/")
    print(f"   • Admin Panel: {BASE_URL}/admin/")
    print(f"   • Sentiment Dashboard: {BASE_URL}/sentiment/dashboard/")
    print(f"   • Signal Dashboard: {BASE_URL}/signals/dashboard/")
    print(f"   • Sentiment API: {BASE_URL}/sentiment/api/sentiment/BTC/")
    print(f"   • Signal API: {BASE_URL}/signals/api/signals/")
    print(f"   • Performance API: {BASE_URL}/signals/api/performance/")
    print(f"   • Market Regime API: {BASE_URL}/signals/api/regimes/")

if __name__ == "__main__":
    main()
