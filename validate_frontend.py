#!/usr/bin/env python3

"""
Frontend validation script for the Indian Cyber Threat Intelligence Platform
"""

import os
import json

def validate_frontend_structure():
    """Validate frontend project structure"""
    print("Validating frontend structure...")
    
    required_files = [
        'frontend/package.json',
        'frontend/public/index.html',
        'frontend/src/index.js',
        'frontend/src/App.js',
        'frontend/src/pages/Dashboard.js',
        'frontend/src/pages/Incidents.js',
        'frontend/src/pages/Analytics.js',
        'frontend/src/pages/Sources.js',
        'frontend/src/pages/Login.js',
        'frontend/src/components/Navbar.js',
        'frontend/src/services/authService.js',
        'frontend/src/contexts/AuthContext.js'
    ]
    
    all_exist = True
    for file_path in required_files:
        if os.path.exists(file_path):
            print(f"✓ {file_path}")
        else:
            print(f"✗ {file_path} missing")
            all_exist = False
    
    return all_exist

def validate_package_json():
    """Validate package.json configuration"""
    print("\nValidating package.json...")
    
    try:
        with open('frontend/package.json', 'r') as f:
            package_data = json.load(f)
        
        required_deps = [
            'react',
            'react-dom',
            'react-router-dom',
            'axios',
            '@mui/material',
            'recharts'
        ]
        
        dependencies = package_data.get('dependencies', {})
        
        all_present = True
        for dep in required_deps:
            if dep in dependencies:
                print(f"✓ {dep}: {dependencies[dep]}")
            else:
                print(f"✗ {dep} missing")
                all_present = False
        
        return all_present
        
    except Exception as e:
        print(f"✗ Error reading package.json: {e}")
        return False

def validate_docker_config():
    """Validate Docker configuration"""
    print("\nValidating Docker configuration...")
    
    docker_files = [
        'docker-compose.yml',
        'docker/Dockerfile.frontend',
        'docker/Dockerfile.backend'
    ]
    
    all_exist = True
    for file_path in docker_files:
        if os.path.exists(file_path):
            print(f"✓ {file_path}")
        else:
            print(f"✗ {file_path} missing")
            all_exist = False
    
    return all_exist

def main():
    """Run frontend validation"""
    print("=" * 60)
    print("Frontend Validation - Indian Cyber Threat Intelligence Platform")
    print("=" * 60)
    
    tests = [
        validate_frontend_structure,
        validate_package_json,
        validate_docker_config
    ]
    
    results = []
    for test in tests:
        results.append(test())
    
    print("\n" + "=" * 60)
    print("FRONTEND VALIDATION SUMMARY")
    print("=" * 60)
    
    if all(results):
        print("✓ All frontend validation tests passed!")
        print("\nNext steps:")
        print("1. Run 'npm install' in the frontend directory")
        print("2. Run 'npm start' to start the development server")
        print("3. Or use 'docker-compose up' to start the full platform")
        return 0
    else:
        print("✗ Some frontend validation tests failed.")
        return 1

if __name__ == "__main__":
    import sys
    sys.exit(main())