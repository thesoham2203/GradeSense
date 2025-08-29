#!/usr/bin/env python3
"""
Test script for GradeSense API
"""

import requests
import os
import json
from pathlib import Path

# API Configuration
API_BASE_URL = "http://localhost:8000"
API_KEY = "test-key"

def test_health_check():
    """Test health check endpoint"""
    print("Testing health check...")
    response = requests.get(f"{API_BASE_URL}/api/v1/health")
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    print("-" * 50)

def test_extract_marksheet(file_path):
    """Test marksheet extraction"""
    print(f"Testing extraction for: {file_path}")
    
    if not os.path.exists(file_path):
        print(f"File not found: {file_path}")
        return
    
    headers = {"Authorization": f"Bearer {API_KEY}"}
    
    with open(file_path, 'rb') as f:
        files = {"file": (os.path.basename(file_path), f)}
        response = requests.post(
            f"{API_BASE_URL}/api/v1/extract",
            headers=headers,
            files=files
        )
    
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        result = response.json()
        print(f"Processing time: {result.get('processing_time', 0):.2f}s")
        print(f"Model used: {result.get('model_used', 'unknown')}")
        print("Extracted data:")
        print(json.dumps(result['data'], indent=2))
    else:
        print(f"Error: {response.text}")
    print("-" * 50)

def test_batch_extract(file_paths):
    """Test batch extraction"""
    print(f"Testing batch extraction for {len(file_paths)} files...")
    
    headers = {"Authorization": f"Bearer {API_KEY}"}
    files = []
    
    for file_path in file_paths:
        if os.path.exists(file_path):
            files.append(("files", (os.path.basename(file_path), open(file_path, 'rb'))))
    
    if not files:
        print("No valid files found for batch processing")
        return
    
    response = requests.post(
        f"{API_BASE_URL}/api/v1/extract/batch",
        headers=headers,
        files=files
    )
    
    # Close file handles
    for _, (_, file_handle) in files:
        file_handle.close()
    
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        result = response.json()
        print(f"Total files: {result.get('total_files', 0)}")
        print(f"Successful: {result.get('successful', 0)}")
        print(f"Failed: {result.get('failed', 0)}")
        print(f"Processing time: {result.get('processing_time', 0):.2f}s")
    else:
        print(f"Error: {response.text}")
    print("-" * 50)

def main():
    """Main test function"""
    print("GradeSense API Test Script")
    print("=" * 50)
    
    # Test health check
    test_health_check()
    
    # Test single file extraction
    test_samples_dir = Path("test_samples")
    if test_samples_dir.exists():
        sample_files = list(test_samples_dir.glob("*"))
        if sample_files:
            for sample_file in sample_files[:2]:  # Test first 2 files
                test_extract_marksheet(str(sample_file))
            
            # Test batch processing
            if len(sample_files) > 1:
                test_batch_extract([str(f) for f in sample_files[:3]])
        else:
            print("No sample files found in test_samples directory")
    else:
        print("test_samples directory not found")
        print("Please create test_samples directory and add sample marksheet files")

if __name__ == "__main__":
    main()
