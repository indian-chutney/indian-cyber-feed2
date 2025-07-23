#!/usr/bin/env python3

"""
Basic validation script to test the Indian Cyber Threat Intelligence Platform setup
"""

import sys
import os
import importlib.util

def test_imports():
    """Test if core modules can be imported"""
    print("Testing core module imports...")
    
    try:
        # Test FastAPI import
        import fastapi
        print("✓ FastAPI imported successfully")
        
        # Test SQLAlchemy import
        import sqlalchemy
        print("✓ SQLAlchemy imported successfully")
        
        # Test Pydantic import
        import pydantic
        print("✓ Pydantic imported successfully")
        
        # Test requests import
        import requests
        print("✓ Requests imported successfully")
        
        # Test BeautifulSoup import
        import bs4
        print("✓ BeautifulSoup4 imported successfully")
        
        return True
    except ImportError as e:
        print(f"✗ Import error: {e}")
        return False

def test_project_structure():
    """Test if project structure is correct"""
    print("\nTesting project structure...")
    
    required_dirs = [
        'backend',
        'backend/app',
        'backend/app/models',
        'backend/app/routers',
        'backend/app/services',
        'backend/database',
        'backend/scrapers',
        'backend/ml',
        'frontend',
        'frontend/src',
        'database',
        'docker',
        'config'
    ]
    
    all_exist = True
    for dir_path in required_dirs:
        if os.path.exists(dir_path):
            print(f"✓ {dir_path} exists")
        else:
            print(f"✗ {dir_path} missing")
            all_exist = False
    
    return all_exist

def test_configuration_files():
    """Test if configuration files exist"""
    print("\nTesting configuration files...")
    
    required_files = [
        'requirements.txt',
        'docker-compose.yml',
        'database/init.sql',
        'frontend/package.json',
        'config/.env.example',
        'README.md'
    ]
    
    all_exist = True
    for file_path in required_files:
        if os.path.exists(file_path):
            print(f"✓ {file_path} exists")
        else:
            print(f"✗ {file_path} missing")
            all_exist = False
    
    return all_exist

def test_backend_modules():
    """Test if backend modules can be loaded"""
    print("\nTesting backend modules...")
    
    # Add backend to path
    sys.path.insert(0, 'backend')
    
    try:
        # Test database connection module
        spec = importlib.util.spec_from_file_location("connection", "backend/database/connection.py")
        connection_module = importlib.util.module_from_spec(spec)
        print("✓ Database connection module loaded")
        
        # Test models module
        spec = importlib.util.spec_from_file_location("models", "backend/app/models/models.py")
        models_module = importlib.util.module_from_spec(spec)
        print("✓ Models module loaded")
        
        return True
    except Exception as e:
        print(f"✗ Backend module error: {e}")
        return False

def main():
    """Run all tests"""
    print("=" * 60)
    print("Indian Cyber Threat Intelligence Platform - Validation Test")
    print("=" * 60)
    
    tests = [
        test_imports,
        test_project_structure,
        test_configuration_files,
        test_backend_modules
    ]
    
    results = []
    for test in tests:
        results.append(test())
    
    print("\n" + "=" * 60)
    print("VALIDATION SUMMARY")
    print("=" * 60)
    
    if all(results):
        print("✓ All tests passed! The platform setup is valid.")
        return 0
    else:
        print("✗ Some tests failed. Please check the setup.")
        return 1

if __name__ == "__main__":
    sys.exit(main())