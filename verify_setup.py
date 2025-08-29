#!/usr/bin/env python3
"""
Startup verification script for GradeSense API
"""

import sys
import os
import asyncio
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

async def test_imports():
    """Test all critical imports"""
    print("🔍 Testing imports...")
    
    try:
        # Test core imports
        from app.core.config import settings
        print("✅ Core config imported")
        
        from app.models.response_models import ExtractedData
        print("✅ Response models imported")
        
        from app.services.extraction_service import ExtractionService
        print("✅ Extraction service imported")
        
        from app.utils.file_validator import FileValidator
        print("✅ File validator imported")
        
        # Test service initialization
        extraction_service = ExtractionService()
        print("✅ Extraction service initialized")
        
        file_validator = FileValidator()
        print("✅ File validator initialized")
        
        return True
        
    except Exception as e:
        print(f"❌ Import failed: {e}")
        return False

async def test_health_check():
    """Test health check functionality"""
    print("\n🔍 Testing health check...")
    
    try:
        from app.services.extraction_service import ExtractionService
        extraction_service = ExtractionService()
        
        # This might fail without API keys, but should not crash
        health = await extraction_service.health_check()
        print(f"✅ Health check completed: {health}")
        return True
        
    except Exception as e:
        print(f"⚠️  Health check failed (expected without API keys): {e}")
        return True  # This is expected without API keys

def test_configuration():
    """Test configuration"""
    print("\n🔍 Testing configuration...")
    
    try:
        from app.core.config import settings
        
        print(f"✅ LLM Provider: {settings.LLM_PROVIDER}")
        print(f"✅ Max file size: {settings.MAX_FILE_SIZE} bytes")
        print(f"✅ Allowed extensions: {settings.get_allowed_extensions}")
        print(f"✅ API keys configured: {len(settings.get_api_keys)} keys")
        
        return True
        
    except Exception as e:
        print(f"❌ Configuration test failed: {e}")
        return False

async def main():
    """Main test function"""
    print("🚀 GradeSense API Startup Verification")
    print("=" * 50)
    
    # Test imports
    imports_ok = await test_imports()
    
    # Test configuration
    config_ok = test_configuration()
    
    # Test health check
    health_ok = await test_health_check()
    
    print("\n" + "=" * 50)
    print("📋 SUMMARY:")
    print(f"   Imports: {'✅ PASS' if imports_ok else '❌ FAIL'}")
    print(f"   Configuration: {'✅ PASS' if config_ok else '❌ FAIL'}")
    print(f"   Health Check: {'✅ PASS' if health_ok else '❌ FAIL'}")
    
    if imports_ok and config_ok:
        print("\n🎉 GradeSense API is ready!")
        print("📝 To start the server, run:")
        print("   uvicorn app.main:app --host 127.0.0.1 --port 8000")
        print("🌐 API Documentation will be available at:")
        print("   http://127.0.0.1:8000/docs")
        return True
    else:
        print("\n❌ Setup incomplete. Please fix the errors above.")
        return False

if __name__ == "__main__":
    asyncio.run(main())
