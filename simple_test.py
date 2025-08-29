"""
Simple test script for GradeSense API using urllib (no external dependencies)
"""

import urllib.request
import json
import os

def test_api_endpoint(url, description):
    """Test an API endpoint"""
    print(f"\n{'='*50}")
    print(f"Testing: {description}")
    print(f"URL: {url}")
    print('='*50)
    
    try:
        with urllib.request.urlopen(url, timeout=10) as response:
            data = response.read().decode('utf-8')
            json_data = json.loads(data)
            
            print(f"Status Code: {response.status}")
            print(f"Response:")
            print(json.dumps(json_data, indent=2))
            
    except Exception as e:
        print(f"Error: {e}")

def main():
    """Main test function"""
    base_url = "http://127.0.0.1:8000"
    
    print("GradeSense API Test Script")
    print("=" * 50)
    
    # Test endpoints
    endpoints = [
        ("/", "Root endpoint"),
        ("/api/v1/health", "Health check endpoint"),
    ]
    
    for endpoint, description in endpoints:
        test_api_endpoint(f"{base_url}{endpoint}", description)
    
    print(f"\n{'='*50}")
    print("Testing completed!")
    print("To test file extraction, you'll need to:")
    print("1. Open a browser and go to: http://127.0.0.1:8000/docs")
    print("2. Use the interactive API documentation")
    print("3. Upload a marksheet file with API key: 'test-key'")
    print('='*50)

if __name__ == "__main__":
    main()
