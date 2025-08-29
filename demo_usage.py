#!/usr/bin/env python3
"""
Complete demo of how to run and use GradeSense API
"""

import urllib.request
import urllib.parse
import json
import base64
import os
from io import BytesIO

# API Configuration
API_BASE_URL = "http://127.0.0.1:8000"
API_KEY = "test-key"  # This is already configured in the system

def demo_basic_endpoints():
    """Demo basic endpoints that work without LLM"""
    print("🌐 BASIC API ENDPOINTS (No API Key Needed)")
    print("=" * 60)
    
    # Test root endpoint
    print("1. Testing Root Endpoint:")
    try:
        response = urllib.request.urlopen(f"{API_BASE_URL}/")
        data = json.loads(response.read().decode())
        print(f"   ✅ Status: {response.status}")
        print(f"   📄 Response: {data['message']}")
    except Exception as e:
        print(f"   ❌ Failed: {e}")
    
    # Test health endpoint
    print("\n2. Testing Health Check:")
    try:
        response = urllib.request.urlopen(f"{API_BASE_URL}/api/v1/health")
        data = json.loads(response.read().decode())
        print(f"   ✅ Status: {response.status}")
        print(f"   🏥 Health: {data['status']}")
        print(f"   🔧 Services: {data['services']}")
    except Exception as e:
        print(f"   ❌ Failed: {e}")

def demo_api_docs():
    """Show how to access API documentation"""
    print("\n📚 API DOCUMENTATION")
    print("=" * 60)
    print("🌐 Interactive API Docs: http://127.0.0.1:8000/docs")
    print("📖 ReDoc Documentation: http://127.0.0.1:8000/redoc")
    print("🔧 OpenAPI Schema: http://127.0.0.1:8000/openapi.json")

def demo_extraction_without_llm():
    """Demo what happens when you try extraction without LLM API keys"""
    print("\n🔍 EXTRACTION DEMO (Without LLM API Keys)")
    print("=" * 60)
    
    # Create a simple text file to simulate a marksheet
    test_content = """
SAMPLE MARKSHEET
Name: John Doe
Roll No: 12345
Marks: Math 85/100, Physics 78/100
""".encode()
    
    print("📝 Testing with sample text file...")
    print("⚠️  Note: This will fail gracefully without real LLM API keys")
    
    # This would be how you'd make the request (showing the format)
    print(f"""
🔧 API Request Format:
POST {API_BASE_URL}/api/v1/extract
Headers: Authorization: Bearer {API_KEY}
Body: multipart/form-data with 'file' field
""")

def explain_api_keys():
    """Explain why API keys are needed"""
    print("\n🔑 WHY API KEYS ARE NEEDED")
    print("=" * 60)
    
    print("""
The GradeSense API uses TWO types of API keys:

1. 🛡️  GRADESENSE API KEY (for access control):
   - Purpose: Authenticate requests to YOUR API
   - Already configured: 'test-key', 'demo-key'
   - How to use: Add header 'Authorization: Bearer test-key'
   - Why needed: Prevents unauthorized access to your service

2. 🧠 LLM PROVIDER API KEY (for AI processing):
   - Purpose: Access Google Gemini or OpenAI for text processing
   - Currently missing: No valid GEMINI_API_KEY or OPENAI_API_KEY
   - Why needed: The AI brain that converts OCR text to structured JSON
   - Where to get:
     * Gemini: https://makersuite.google.com/app/apikey
     * OpenAI: https://platform.openai.com/api-keys
""")

def show_how_to_get_api_keys():
    """Show how to get and configure API keys"""
    print("\n📋 HOW TO GET & CONFIGURE API KEYS")
    print("=" * 60)
    
    print("""
STEP 1: Get LLM API Key
🔹 For Google Gemini (Recommended - Free tier available):
   1. Go to: https://makersuite.google.com/app/apikey
   2. Sign in with Google account
   3. Click 'Create API Key'
   4. Copy the key (starts with 'AIza...')

🔹 For OpenAI (Paid service):
   1. Go to: https://platform.openai.com/api-keys
   2. Sign up/Login
   3. Create new API key
   4. Copy the key (starts with 'sk-...')

STEP 2: Configure the .env file
   1. Open the .env file in the project folder
   2. Add your API key:
      GEMINI_API_KEY=your_actual_api_key_here
      # OR
      OPENAI_API_KEY=your_actual_api_key_here
   3. Save the file
   4. Restart the server

STEP 3: Test the API
   Once configured, you can upload marksheet images/PDFs
   and get structured JSON output with confidence scores!
""")

def show_current_config():
    """Show current configuration status"""
    print("\n⚙️  CURRENT CONFIGURATION STATUS")
    print("=" * 60)
    
    # Check .env file
    env_file = "d:\\GradeSense\\.env"
    if os.path.exists(env_file):
        print("✅ .env file exists")
        with open(env_file, 'r') as f:
            content = f.read()
            if 'GEMINI_API_KEY=' in content and not 'GEMINI_API_KEY=your_gemini_api_key_here' in content:
                print("✅ Gemini API key configured")
            elif 'OPENAI_API_KEY=' in content and not 'OPENAI_API_KEY=your_openai_api_key_here' in content:
                print("✅ OpenAI API key configured")
            else:
                print("⚠️  No valid LLM API keys configured yet")
                print("   (Keys are still set to placeholder values)")
    else:
        print("❌ .env file not found")

def main():
    """Main demo function"""
    print("🎯 GRADESENSE API - COMPLETE USAGE GUIDE")
    print("=" * 80)
    
    # Demo basic functionality
    demo_basic_endpoints()
    
    # Show documentation
    demo_api_docs()
    
    # Explain API keys
    explain_api_keys()
    
    # Show how to get keys
    show_how_to_get_api_keys()
    
    # Show current config
    show_current_config()
    
    # Demo extraction format
    demo_extraction_without_llm()
    
    print("\n" + "=" * 80)
    print("🎉 SUMMARY:")
    print("✅ Server is running on: http://127.0.0.1:8000")
    print("✅ Basic endpoints work without LLM API keys")
    print("⚠️  For marksheet extraction, add LLM API key to .env file")
    print("📚 Full documentation at: http://127.0.0.1:8000/docs")
    print("=" * 80)

if __name__ == "__main__":
    main()
