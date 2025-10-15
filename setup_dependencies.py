#!/usr/bin/env python3
"""
Requirements and Dependencies Update Script
Ensures all required packages are installed for Phase 5 functionality
"""

import os
import sys
import subprocess
from datetime import datetime

# Add the project directory to Python path
project_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_dir)

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

def update_requirements():
    """Update requirements.txt with all necessary packages"""
    print_status("=== UPDATING REQUIREMENTS ===", "FIXING")
    
    # Enhanced requirements for Phase 5
    requirements_content = """# Core Django and Web Framework
Django>=4.2.0,<5.0.0
djangorestframework>=3.14.0
django-cors-headers>=4.0.0
django-extensions>=3.2.0

# Database
psycopg2-binary>=2.9.0
sqlite3

# Celery for Task Queue
celery>=5.3.0
django-celery-beat>=2.5.0
django-celery-results>=2.5.0
kombu>=5.3.0
redis>=4.5.0

# Data Processing and Analysis
pandas>=2.0.0
numpy>=1.24.0
scipy>=1.10.0
scikit-learn>=1.3.0

# Machine Learning and Deep Learning
tensorflow>=2.13.0
keras>=2.13.0
torch>=2.0.0
torchvision>=0.15.0
xgboost>=1.7.0
lightgbm>=4.0.0

# Technical Analysis
ta-lib>=0.4.0
mplfinance>=0.12.0
matplotlib>=3.7.0
seaborn>=0.12.0
plotly>=5.15.0

# Image Processing for Chart Analysis
Pillow>=10.0.0
opencv-python>=4.8.0
imageio>=2.31.0

# Web Scraping and API
requests>=2.31.0
beautifulsoup4>=4.12.0
selenium>=4.11.0
websocket-client>=1.6.0

# Cryptocurrency APIs
ccxt>=4.0.0
python-binance>=1.0.0

# Sentiment Analysis
textblob>=0.17.0
vaderSentiment>=3.3.0
transformers>=4.30.0

# Data Visualization
dash>=2.12.0
dash-bootstrap-components>=1.4.0

# Monitoring and Logging
flower>=2.0.0
sentry-sdk>=1.30.0

# Development and Testing
pytest>=7.4.0
pytest-django>=4.5.0
pytest-cov>=4.1.0
black>=23.0.0
flake8>=6.0.0
isort>=5.12.0

# Production Deployment
gunicorn>=21.2.0
whitenoise>=6.5.0
supervisor>=4.2.0

# Environment Management
python-dotenv>=1.0.0

# Additional Utilities
python-dateutil>=2.8.0
pytz>=2023.3
cryptography>=41.0.0
pyjwt>=2.8.0
"""
    
    # Write requirements file
    requirements_file = os.path.join(project_dir, 'requirements.txt')
    with open(requirements_file, 'w') as f:
        f.write(requirements_content)
    
    print_status("Requirements.txt updated!", "SUCCESS")

def install_packages():
    """Install all required packages"""
    print_status("=== INSTALLING PACKAGES ===", "FIXING")
    
    try:
        # Upgrade pip first
        print_status("Upgrading pip...", "INFO")
        subprocess.run([sys.executable, '-m', 'pip', 'install', '--upgrade', 'pip'], 
                      check=True, capture_output=True)
        print_status("Pip upgraded!", "SUCCESS")
        
        # Install requirements
        print_status("Installing requirements...", "INFO")
        requirements_file = os.path.join(project_dir, 'requirements.txt')
        subprocess.run([sys.executable, '-m', 'pip', 'install', '-r', requirements_file], 
                      check=True, capture_output=True)
        print_status("Requirements installed!", "SUCCESS")
        
        return True
        
    except subprocess.CalledProcessError as e:
        print_status(f"Failed to install packages: {e}", "ERROR")
        print_status("You may need to install packages manually", "WARNING")
        return False
    except Exception as e:
        print_status(f"Error installing packages: {e}", "ERROR")
        return False

def create_install_script():
    """Create a comprehensive installation script"""
    install_script = """#!/bin/bash
# Comprehensive Installation Script for AI Trading Engine

echo "========================================"
echo "AI Trading Engine - Installation Script"
echo "========================================"
echo ""

# Check Python version
echo "Checking Python version..."
python_version=$(python3 --version 2>&1)
echo "Found: $python_version"

if [[ $python_version == *"3.8"* ]] || [[ $python_version == *"3.9"* ]] || [[ $python_version == *"3.10"* ]] || [[ $python_version == *"3.11"* ]]; then
    echo "✅ Python version is compatible"
else
    echo "❌ Python 3.8+ is required"
    exit 1
fi

echo ""

# Create virtual environment
echo "Creating virtual environment..."
if [ ! -d "venv" ]; then
    python3 -m venv venv
    echo "✅ Virtual environment created"
else
    echo "✅ Virtual environment already exists"
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo "Upgrading pip..."
pip install --upgrade pip

# Install requirements
echo "Installing requirements..."
pip install -r requirements.txt

# Install TA-Lib (special case)
echo "Installing TA-Lib..."
if command -v brew &> /dev/null; then
    # macOS
    brew install ta-lib
    pip install TA-Lib
elif command -v apt-get &> /dev/null; then
    # Ubuntu/Debian
    sudo apt-get install libta-lib-dev
    pip install TA-Lib
elif command -v yum &> /dev/null; then
    # CentOS/RHEL
    sudo yum install ta-lib-devel
    pip install TA-Lib
else
    echo "⚠️ Please install TA-Lib manually for your system"
fi

echo ""
echo "========================================"
echo "Installation Complete!"
echo "========================================"
echo ""
echo "Next steps:"
echo "1. Activate virtual environment: source venv/bin/activate"
echo "2. Run database setup: python setup_database_phase5.py"
echo "3. Fix signal generation: python fix_signal_generation_issues.py"
echo "4. Start Celery: ./start_celery_worker.sh & ./start_celery_beat.sh"
echo ""
"""
    
    # Write installation script
    install_file = os.path.join(project_dir, 'install.sh')
    with open(install_file, 'w') as f:
        f.write(install_script)
    
    # Make executable
    os.chmod(install_file, 0o755)
    
    print_status("Installation script created: install.sh", "SUCCESS")

def create_windows_install_script():
    """Create Windows installation script"""
    windows_install = """@echo off
echo ========================================
echo AI Trading Engine - Windows Installation
echo ========================================
echo.

REM Check Python version
echo Checking Python version...
python --version
if %errorlevel% neq 0 (
    echo Error: Python is not installed or not in PATH
    pause
    exit /b 1
)

echo.

REM Create virtual environment
echo Creating virtual environment...
if not exist "venv" (
    python -m venv venv
    echo Virtual environment created
) else (
    echo Virtual environment already exists
)

REM Activate virtual environment
echo Activating virtual environment...
call venv\\Scripts\\activate.bat

REM Upgrade pip
echo Upgrading pip...
python -m pip install --upgrade pip

REM Install requirements
echo Installing requirements...
pip install -r requirements.txt

REM Install TA-Lib (Windows)
echo Installing TA-Lib...
pip install TA-Lib

echo.
echo ========================================
echo Installation Complete!
echo ========================================
echo.
echo Next steps:
echo 1. Activate virtual environment: venv\\Scripts\\activate.bat
echo 2. Run database setup: python setup_database_phase5.py
echo 3. Fix signal generation: python fix_signal_generation_issues.py
echo 4. Start Celery: start_celery_worker.bat and start_celery_beat.bat
echo.
pause
"""
    
    # Write Windows installation script
    windows_file = os.path.join(project_dir, 'install.bat')
    with open(windows_file, 'w') as f:
        f.write(windows_install)
    
    print_status("Windows installation script created: install.bat", "SUCCESS")

def check_installed_packages():
    """Check which packages are already installed"""
    print_status("=== CHECKING INSTALLED PACKAGES ===", "FIXING")
    
    critical_packages = [
        'django', 'celery', 'pandas', 'numpy', 'tensorflow', 
        'matplotlib', 'requests', 'redis', 'psycopg2'
    ]
    
    missing_packages = []
    
    for package in critical_packages:
        try:
            __import__(package)
            print_status(f"✅ {package} is installed", "SUCCESS")
        except ImportError:
            print_status(f"❌ {package} is missing", "ERROR")
            missing_packages.append(package)
    
    if missing_packages:
        print_status(f"Missing packages: {', '.join(missing_packages)}", "WARNING")
        return False
    else:
        print_status("All critical packages are installed!", "SUCCESS")
        return True

def main():
    """Main function to setup requirements and dependencies"""
    print_status("=== REQUIREMENTS AND DEPENDENCIES SETUP ===", "INFO")
    print_status("This script will update requirements and ensure all dependencies are installed", "INFO")
    print()
    
    # Update requirements
    update_requirements()
    
    # Check installed packages
    packages_ok = check_installed_packages()
    
    # Install packages if needed
    if not packages_ok:
        install_packages()
    
    # Create installation scripts
    create_install_script()
    create_windows_install_script()
    
    print()
    print_status("=== DEPENDENCIES SETUP COMPLETE ===", "SUCCESS")
    print_status("Next steps:", "INFO")
    print_status("1. Run: python setup_database_phase5.py", "INFO")
    print_status("2. Run: python fix_signal_generation_issues.py", "INFO")
    print_status("3. Start Celery workers", "INFO")
    
    print()
    print_status("Dependencies setup completed!", "INFO")

if __name__ == "__main__":
    main()



































