# Playwright configuration for AI Trading Engine
import os
from pathlib import Path

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent

def get_project_root():
    return BASE_DIR

# Playwright configuration
PLAYWRIGHT_CONFIG = {
    'browsers': ['chromium'],  # Can add 'firefox', 'webkit' for cross-browser testing
    'headless': False,  # Set to True for CI/CD environments
    'slow_mo': 500,  # Slow down actions for visibility during development
    'timeout': 30000,  # 30 seconds timeout
    'retries': 2,  # Retry failed tests
    'workers': 1,  # Number of parallel workers
    'viewport': {
        'width': 1920,
        'height': 1080
    },
    'video': {
        'mode': 'on-first-retry',  # Record video on retry
        'size': {'width': 1920, 'height': 1080}
    },
    'screenshot': {
        'mode': 'on',  # Take screenshots on every action
        'full_page': True
    },
    'trace': {
        'mode': 'on-first-retry'  # Record trace on retry
    }
}

# Test URLs
TEST_URLS = {
    'base_url': 'http://127.0.0.1:8000',
    'home': '/',
    'login': '/login/',
    'dashboard': '/dashboard/',
    'portfolio': '/portfolio/',
    'signals': '/signals/',
    'analytics': '/analytics/',
    'analytics_performance': '/analytics/performance/',
    'analytics_risk': '/analytics/risk/',
    'analytics_backtesting': '/analytics/backtesting/',
    'analytics_ml': '/analytics/ml/',
    'subscription': '/subscription/choice/',
    'admin': '/admin/'
}

# Test credentials
TEST_CREDENTIALS = {
    'admin': {
        'username': 'admin',
        'password': 'admin123'
    },
    'testuser': {
        'username': 'testuser',
        'password': 'testpass123'
    }
}

# Test data
TEST_DATA = {
    'crypto_symbols': ['BTC', 'ETH', 'ADA', 'DOT', 'LINK'],
    'timeframes': ['1h', '4h', '1d', '1w'],
    'portfolio_assets': ['Bitcoin', 'Ethereum', 'Cardano']
}

# Test directories
TEST_DIRS = {
    'videos': BASE_DIR / 'test_videos',
    'screenshots': BASE_DIR / 'test_screenshots',
    'traces': BASE_DIR / 'test_traces',
    'reports': BASE_DIR / 'test_reports'
}

# Create test directories if they don't exist
for dir_path in TEST_DIRS.values():
    dir_path.mkdir(exist_ok=True)

# Test configuration functions
def get_browser_config(browser_name='chromium'):
    """Get browser-specific configuration"""
    base_config = {
        'headless': PLAYWRIGHT_CONFIG['headless'],
        'slow_mo': PLAYWRIGHT_CONFIG['slow_mo'],
        'args': [
            '--start-maximized',
            '--disable-web-security',
            '--disable-features=VizDisplayCompositor',
            '--no-sandbox',
            '--disable-dev-shm-usage'
        ]
    }
    
    if browser_name == 'firefox':
        base_config['args'].extend(['--width=1920', '--height=1080'])
    elif browser_name == 'webkit':
        base_config['args'].extend(['--no-sandbox'])
    
    return base_config

def get_context_config():
    """Get context configuration"""
    return {
        'viewport': PLAYWRIGHT_CONFIG['viewport'],
        'record_video_dir': str(TEST_DIRS['videos']),
        'record_har_path': str(TEST_DIRS['reports'] / 'test_results.har'),
        'ignore_https_errors': True,
        'java_script_enabled': True
    }

def get_page_config():
    """Get page configuration"""
    return {
        'timeout': PLAYWRIGHT_CONFIG['timeout'],
        'wait_until': 'networkidle'
    }

# Export configuration
if __name__ == "__main__":
    print("Playwright Configuration for AI Trading Engine")
    print("=" * 50)
    print(f"Base URL: {TEST_URLS['base_url']}")
    print(f"Test Credentials: {list(TEST_CREDENTIALS.keys())}")
    print(f"Test Directories: {list(TEST_DIRS.keys())}")
    print(f"Browser Config: {get_browser_config()}")
    print("=" * 50)
