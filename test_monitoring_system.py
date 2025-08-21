#!/usr/bin/env python3
"""
Test Script for Phase 7B.3 - Monitoring & Alerting System

This script tests the comprehensive monitoring and alerting system
including application monitoring, error alerting, and uptime monitoring.
"""

import requests
import json
import time
import sys
from datetime import datetime

# Configuration
BASE_URL = "http://localhost:8000"  # Adjust if your server runs on different port
HEALTH_ENDPOINT = f"{BASE_URL}/health/"
MONITORING_DASHBOARD = f"{BASE_URL}/api/monitoring/dashboard/"
START_MONITORING = f"{BASE_URL}/api/monitoring/start/"
STOP_MONITORING = f"{BASE_URL}/api/monitoring/stop/"
PERFORMANCE_METRICS = f"{BASE_URL}/api/monitoring/performance/"
SERVICE_STATUS = f"{BASE_URL}/api/monitoring/services/"
ALERT_HISTORY = f"{BASE_URL}/api/monitoring/alerts/"
TEST_ALERT = f"{BASE_URL}/api/monitoring/test-alert/"

def print_header(title):
    """Print a formatted header"""
    print("\n" + "="*60)
    print(f" {title}")
    print("="*60)

def print_section(title):
    """Print a formatted section"""
    print(f"\n--- {title} ---")

def test_health_endpoint():
    """Test the main health check endpoint"""
    print_section("Testing Health Check Endpoint")
    
    try:
        response = requests.get(HEALTH_ENDPOINT, timeout=10)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"Overall Status: {data.get('status', 'unknown')}")
            print(f"Timestamp: {data.get('timestamp', 'unknown')}")
            
            services = data.get('services', {})
            print("\nService Status:")
            for service, status in services.items():
                if isinstance(status, dict):
                    print(f"  {service}:")
                    for metric, value in status.items():
                        if isinstance(value, dict):
                            print(f"    {metric}: {value}")
                        else:
                            print(f"    {metric}: {value}")
                else:
                    print(f"  {service}: {status}")
                    
            monitoring = data.get('monitoring', {})
            print("\nMonitoring Status:")
            for service, active in monitoring.items():
                print(f"  {service}: {'Active' if active else 'Inactive'}")
                
        else:
            print(f"Error: {response.text}")
            
    except requests.exceptions.RequestException as e:
        print(f"Error connecting to health endpoint: {e}")
        return False
        
    return True

def test_monitoring_dashboard():
    """Test the monitoring dashboard endpoint"""
    print_section("Testing Monitoring Dashboard")
    
    try:
        response = requests.get(MONITORING_DASHBOARD, timeout=10)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"Timestamp: {data.get('timestamp', 'unknown')}")
            
            # Check application monitoring
            app_monitoring = data.get('application_monitoring', {})
            if app_monitoring:
                print(f"\nApplication Monitoring:")
                print(f"  Active: {app_monitoring.get('monitoring_active', False)}")
                print(f"  Last Check: {app_monitoring.get('last_check', 'unknown')}")
                print(f"  Alert Count: {app_monitoring.get('alert_count', 0)}")
                
            # Check error alerting
            error_alerting = data.get('error_alerting', {})
            if error_alerting:
                print(f"\nError Alerting:")
                print(f"  Error Counts: {error_alerting.get('error_counts', {})}")
                print(f"  Alert Count: {error_alerting.get('alert_count', 0)}")
                
            # Check uptime monitoring
            uptime_monitoring = data.get('uptime_monitoring', {})
            if uptime_monitoring:
                print(f"\nUptime Monitoring:")
                print(f"  Active: {uptime_monitoring.get('monitoring_active', False)}")
                print(f"  Start Time: {uptime_monitoring.get('start_time', 'unknown')}")
                print(f"  Availability: {uptime_monitoring.get('availability_percentage', 0):.1f}%")
                
        else:
            print(f"Error: {response.text}")
            
    except requests.exceptions.RequestException as e:
        print(f"Error connecting to monitoring dashboard: {e}")
        return False
        
    return True

def test_start_monitoring():
    """Test starting monitoring services"""
    print_section("Testing Start Monitoring")
    
    try:
        response = requests.post(START_MONITORING, timeout=10)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"Message: {data.get('message', 'No message')}")
            print(f"Status: {data.get('status', 'Unknown')}")
            print(f"Timestamp: {data.get('timestamp', 'Unknown')}")
            return True
        else:
            print(f"Error: {response.text}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"Error starting monitoring: {e}")
        return False

def test_stop_monitoring():
    """Test stopping monitoring services"""
    print_section("Testing Stop Monitoring")
    
    try:
        response = requests.post(STOP_MONITORING, timeout=10)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"Message: {data.get('message', 'No message')}")
            print(f"Status: {data.get('status', 'Unknown')}")
            print(f"Timestamp: {data.get('timestamp', 'Unknown')}")
            return True
        else:
            print(f"Error: {response.text}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"Error stopping monitoring: {e}")
        return False

def test_performance_metrics():
    """Test performance metrics endpoint"""
    print_section("Testing Performance Metrics")
    
    try:
        response = requests.get(PERFORMANCE_METRICS, timeout=10)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"Timestamp: {data.get('timestamp', 'unknown')}")
            
            current_metrics = data.get('current_metrics', {})
            if current_metrics:
                print(f"\nCurrent Metrics:")
                print(f"  CPU: {current_metrics.get('cpu_percent', 0):.1f}%")
                print(f"  Memory: {current_metrics.get('memory_percent', 0):.1f}%")
                print(f"  Disk: {current_metrics.get('disk_percent', 0):.1f}%")
                
            summary = data.get('summary', {})
            if summary:
                print(f"\nPerformance Summary:")
                for metric, info in summary.items():
                    if isinstance(info, dict):
                        print(f"  {metric}:")
                        print(f"    Current: {info.get('current', 0):.1f}")
                        print(f"    Average: {info.get('average', 0):.1f}")
                        print(f"    Trend: {info.get('trend', 'unknown')}")
                        
        else:
            print(f"Error: {response.text}")
            
    except requests.exceptions.RequestException as e:
        print(f"Error getting performance metrics: {e}")
        return False
        
    return True

def test_service_status():
    """Test service status endpoint"""
    print_section("Testing Service Status")
    
    try:
        response = requests.get(SERVICE_STATUS, timeout=10)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"Timestamp: {data.get('timestamp', 'unknown')}")
            
            service_status = data.get('service_status', {})
            if service_status:
                print(f"\nService Status:")
                for service, status in service_status.items():
                    print(f"  {service}: {status}")
                    
            uptime_data = data.get('uptime_data', {})
            if uptime_data:
                print(f"\nUptime Data:")
                print(f"  Active: {uptime_data.get('monitoring_active', False)}")
                print(f"  Start Time: {uptime_data.get('start_time', 'unknown')}")
                print(f"  Uptime Records: {uptime_data.get('uptime_records', 0)}")
                print(f"  Downtime Events: {uptime_data.get('downtime_events', 0)}")
                
        else:
            print(f"Error: {response.text}")
            
    except requests.exceptions.RequestException as e:
        print(f"Error getting service status: {e}")
        return False
        
    return True

def test_alert_history():
    """Test alert history endpoint"""
    print_section("Testing Alert History")
    
    try:
        response = requests.get(ALERT_HISTORY, timeout=10)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"Timestamp: {data.get('timestamp', 'unknown')}")
            
            app_alerts = data.get('application_alerts', [])
            print(f"\nApplication Alerts: {len(app_alerts)}")
            for alert in app_alerts[:3]:  # Show first 3 alerts
                print(f"  {alert.get('type', 'Unknown')}: {alert.get('severity', 'Unknown')}")
                
            error_alerts = data.get('error_alerts', [])
            print(f"\nError Alerts: {len(error_alerts)}")
            for alert in error_alerts[:3]:  # Show first 3 alerts
                print(f"  {alert.get('type', 'Unknown')}: {alert.get('level', 'Unknown')}")
                
        else:
            print(f"Error: {response.text}")
            
    except requests.exceptions.RequestException as e:
        print(f"Error getting alert history: {e}")
        return False
        
    return True

def test_trigger_alert():
    """Test triggering a test alert"""
    print_section("Testing Test Alert")
    
    try:
        response = requests.post(TEST_ALERT, timeout=10)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"Message: {data.get('message', 'No message')}")
            print(f"Timestamp: {data.get('timestamp', 'Unknown')}")
            return True
        else:
            print(f"Error: {response.text}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"Error triggering test alert: {e}")
        return False

def run_comprehensive_test():
    """Run all tests"""
    print_header("Phase 7B.3 - Monitoring & Alerting System Test")
    print(f"Testing against: {BASE_URL}")
    print(f"Test started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    test_results = []
    
    # Test health endpoint
    test_results.append(("Health Endpoint", test_health_endpoint()))
    
    # Test monitoring dashboard
    test_results.append(("Monitoring Dashboard", test_monitoring_dashboard()))
    
    # Test starting monitoring
    test_results.append(("Start Monitoring", test_start_monitoring()))
    
    # Wait a moment for monitoring to start
    time.sleep(2)
    
    # Test performance metrics
    test_results.append(("Performance Metrics", test_performance_metrics()))
    
    # Test service status
    test_results.append(("Service Status", test_service_status()))
    
    # Test alert history
    test_results.append(("Alert History", test_alert_history()))
    
    # Test triggering test alert
    test_results.append(("Test Alert", test_trigger_alert()))
    
    # Wait a moment for alert to be processed
    time.sleep(2)
    
    # Test stopping monitoring
    test_results.append(("Stop Monitoring", test_stop_monitoring()))
    
    # Print summary
    print_header("Test Results Summary")
    
    passed = 0
    total = len(test_results)
    
    for test_name, result in test_results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} - {test_name}")
        if result:
            passed += 1
            
    print(f"\nOverall Result: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Monitoring system is working correctly.")
        return True
    else:
        print("⚠️ Some tests failed. Please check the system configuration.")
        return False

if __name__ == "__main__":
    try:
        success = run_comprehensive_test()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\nTest interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\nUnexpected error: {e}")
        sys.exit(1)
