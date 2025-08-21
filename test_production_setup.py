#!/usr/bin/env python3
"""
Test script for Production Server Setup (Phase 7B.1)

This script verifies that all production configuration files are properly
formatted and accessible.
"""

import os
import sys
import json
from pathlib import Path

def test_file_exists(file_path, description):
    """Test if a file exists and is readable"""
    try:
        if os.path.exists(file_path):
            with open(file_path, 'r') as f:
                content = f.read()
            print(f"✅ {description}: {file_path} (Size: {len(content)} bytes)")
            return True
        else:
            print(f"❌ {description}: {file_path} - FILE NOT FOUND")
            return False
    except Exception as e:
        print(f"❌ {description}: {file_path} - ERROR: {e}")
        return False

def test_python_syntax(file_path, description):
    """Test if a Python file has valid syntax"""
    try:
        with open(file_path, 'r') as f:
            content = f.read()
        compile(content, file_path, 'exec')
        print(f"✅ {description}: {file_path} - Python syntax valid")
        return True
    except SyntaxError as e:
        print(f"❌ {description}: {file_path} - Python syntax error: {e}")
        return False
    except Exception as e:
        print(f"❌ {description}: {file_path} - Error: {e}")
        return False

def test_json_syntax(file_path, description):
    """Test if a file has valid JSON syntax"""
    try:
        with open(file_path, 'r') as f:
            json.load(f)
        print(f"✅ {description}: {file_path} - JSON syntax valid")
        return True
    except json.JSONDecodeError as e:
        print(f"❌ {description}: {file_path} - JSON syntax error: {e}")
        return False
    except Exception as e:
        print(f"❌ {description}: {file_path} - Error: {e}")
        return False

def test_nginx_config(file_path, description):
    """Test if Nginx configuration file has basic structure"""
    try:
        with open(file_path, 'r') as f:
            content = f.read()
        
        # Check for basic Nginx directives
        required_directives = ['server', 'listen', 'location']
        missing_directives = []
        
        for directive in required_directives:
            if directive not in content:
                missing_directives.append(directive)
        
        if missing_directives:
            print(f"⚠️  {description}: {file_path} - Missing directives: {missing_directives}")
            return False
        else:
            print(f"✅ {description}: {file_path} - Basic structure valid")
            return True
            
    except Exception as e:
        print(f"❌ {description}: {file_path} - Error: {e}")
        return False

def test_supervisor_config(file_path, description):
    """Test if Supervisor configuration file has basic structure"""
    try:
        with open(file_path, 'r') as f:
            content = f.read()
        
        # Check for basic Supervisor sections
        required_sections = ['supervisord', 'program:', 'group:']
        missing_sections = []
        
        for section in required_sections:
            if section not in content:
                missing_sections.append(section)
        
        if missing_sections:
            print(f"⚠️  {description}: {file_path} - Missing sections: {missing_sections}")
            return False
        else:
            print(f"✅ {description}: {file_path} - Basic structure valid")
            return True
            
    except Exception as e:
        print(f"❌ {description}: {file_path} - Error: {e}")
        return False

def test_gunicorn_config(file_path, description):
    """Test if Gunicorn configuration file has basic structure"""
    try:
        with open(file_path, 'r') as f:
            content = f.read()
        
        # Check for basic Gunicorn settings
        required_settings = ['bind', 'workers', 'worker_class']
        missing_settings = []
        
        for setting in required_settings:
            if setting not in content:
                missing_settings.append(setting)
        
        if missing_settings:
            print(f"⚠️  {description}: {file_path} - Missing settings: {missing_settings}")
            return False
        else:
            print(f"✅ {description}: {file_path} - Basic structure valid")
            return True
            
    except Exception as e:
        print(f"❌ {description}: {file_path} - Error: {e}")
        return False

def test_environment_file(file_path, description):
    """Test if environment file has basic structure"""
    try:
        with open(file_path, 'r') as f:
            content = f.read()
        
        # Check for key environment variables
        required_vars = ['DEBUG', 'SECRET_KEY', 'DB_NAME', 'REDIS_HOST']
        missing_vars = []
        
        for var in required_vars:
            if var not in content:
                missing_vars.append(var)
        
        if missing_vars:
            print(f"⚠️  {description}: {file_path} - Missing variables: {missing_vars}")
            return False
        else:
            print(f"✅ {description}: {file_path} - Basic structure valid")
            return True
            
    except Exception as e:
        print(f"❌ {description}: {file_path} - Error: {e}")
        return False

def main():
    """Main test function"""
    print("🔍 Testing Production Server Setup Configuration Files")
    print("=" * 60)
    
    # Get current directory
    current_dir = Path.cwd()
    
    # Test files
    test_results = []
    
    # Test production settings
    prod_settings = current_dir / "ai_trading_engine" / "settings_production.py"
    test_results.append(test_python_syntax(prod_settings, "Production Settings"))
    
    # Test Gunicorn config
    gunicorn_config = current_dir / "gunicorn.conf.py"
    test_results.append(test_gunicorn_config(gunicorn_config, "Gunicorn Configuration"))
    
    # Test Nginx config
    nginx_config = current_dir / "nginx.conf"
    test_results.append(test_nginx_config(nginx_config, "Nginx Configuration"))
    
    # Test Supervisor config
    supervisor_config = current_dir / "supervisor.conf"
    test_results.append(test_supervisor_config(supervisor_config, "Supervisor Configuration"))
    
    # Test environment file
    env_file = current_dir / "env.production"
    test_results.append(test_environment_file(env_file, "Production Environment"))
    
    # Test deployment script
    deploy_script = current_dir / "deploy_production.sh"
    test_results.append(test_file_exists(deploy_script, "Deployment Script"))
    
    # Test production documentation
    prod_docs = current_dir / "PRODUCTION_DEPLOYMENT.md"
    test_results.append(test_file_exists(prod_docs, "Production Documentation"))
    
    # Test health check command
    health_check_cmd = current_dir / "apps" / "core" / "management" / "commands" / "health_check.py"
    test_results.append(test_python_syntax(health_check_cmd, "Health Check Command"))
    
    # Test requirements file
    requirements = current_dir / "requirements.txt"
    test_results.append(test_file_exists(requirements, "Requirements File"))
    
    print("\n" + "=" * 60)
    print("📊 Test Results Summary")
    print("=" * 60)
    
    passed = sum(test_results)
    total = len(test_results)
    
    print(f"Total Tests: {total}")
    print(f"Passed: {passed}")
    print(f"Failed: {total - passed}")
    print(f"Success Rate: {(passed/total)*100:.1f}%")
    
    if passed == total:
        print("\n🎉 All production configuration files are properly configured!")
        print("✅ Phase 7B.1: Production Server Setup is ready for deployment")
    else:
        print(f"\n⚠️  {total - passed} configuration files need attention")
        print("Please review the failed tests above")
    
    print("\n📋 Next Steps:")
    print("1. Update environment variables in env.production")
    print("2. Customize domain names in nginx.conf")
    print("3. Update paths in supervisor.conf and deploy_production.sh")
    print("4. Run deploy_production.sh on your production server")
    print("5. Verify deployment with health checks")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
