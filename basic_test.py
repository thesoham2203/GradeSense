#!/usr/bin/env python3
"""
Simple test script for GradeSense API using built-in libraries
"""

import urllib.request
import urllib.parse
import json
import os

# API Configuration
API_BASE_URL = "http://127.0.0.1:8000"

def test_health_check():
    """Test health check endpoint"""
    print("Testing health check...")
    try:
        response = urllib.request.urlopen(f"{API_BASE_URL}/api/v1/health")
        data = json.loads(response.read().decode())
        print(f"Status: {response.status}")
        print(f"Response: {json.dumps(data, indent=2)}")
        return True
    except Exception as e:
        print(f"Health check failed: {e}")
        return False

def test_root_endpoint():
    """Test root endpoint"""
    print("\nTesting root endpoint...")
    try:
        response = urllib.request.urlopen(f"{API_BASE_URL}/")
        data = json.loads(response.read().decode())
        print(f"Status: {response.status}")
        print(f"Response: {json.dumps(data, indent=2)}")
        return True
    except Exception as e:
        print(f"Root endpoint test failed: {e}")
        return False

def main():
    """Main test function"""
    print("GradeSense API Simple Test")
    print("=" * 40)
    
    # Test health check
    health_ok = test_health_check()
    
    # Test root endpoint
    root_ok = test_root_endpoint()
    
    print("\n" + "=" * 40)
    if health_ok and root_ok:
        print("✅ Basic API tests passed!")
        print("🌐 API Documentation: http://127.0.0.1:8000/docs")
        print("🔗 API Base URL: http://127.0.0.1:8000")
    else:
        print("❌ Some tests failed")

if __name__ == "__main__":
    main()
