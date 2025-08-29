"""
Railway-compatible main application
"""

import os
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException, Depends, UploadFile, File, Header
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import logging
from typing import Optional, List

# Try to import services, fall back to Railway-compatible versions
try:
    from app.services.extraction_service import ExtractionService
    from app.services.ocr_service import OCRService
    FULL_FEATURES = True
except ImportError:
    from app.services.railway_ocr_service import RailwayOCRService
    FULL_FEATURES = False

from app.core.config import settings
from app.models.response import (
    ExtractionResponse, 
    BatchExtractionResponse, 
    HealthResponse,
    ErrorResponse
)
from app.utils.file_validator import FileValidator

# Setup logging
logging.basicConfig(level=getattr(logging, settings.LOG_LEVEL.upper()))
logger = logging.getLogger(__name__)

# Global services
extraction_service = None
file_validator = FileValidator()

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan management"""
    global extraction_service
    
    try:
        if FULL_FEATURES:
            extraction_service = ExtractionService()
            logger.info("Full-featured extraction service initialized")
        else:
            # Railway demo mode
            ocr_service = RailwayOCRService()
            extraction_service = type('DemoExtractionService', (), {
                'extract_marksheet_data': lambda self, file_data, filename: {
                    "extracted_data": {
                        "student_name": "Demo Student",
                        "roll_number": "DEMO123",
                        "class": "Demo Class",
                        "subjects": ["Math: 85", "Science: 90", "English: 78"],
                        "total_marks": "253/300",
                        "grade": "A"
                    },
                    "confidence_scores": {
                        "overall": 0.95,
                        "student_name": 0.98,
                        "roll_number": 0.95,
                        "subjects": 0.92
                    },
                    "processing_info": {
                        "mode": "railway_demo",
                        "message": "This is a demo response for Railway deployment"
                    }
                },
                'get_health_status': lambda self: {
                    "ocr_service": "railway_demo",
                    "llm_service": "available" if settings.GEMINI_API_KEY else "not_configured",
                    "status": "healthy"
                }
            })()
            logger.info("Railway demo extraction service initialized")
            
        logger.info("Application startup complete")
        yield
        
    except Exception as e:
        logger.error(f"Startup error: {e}")
        yield
    finally:
        logger.info("Application shutdown")

# Create FastAPI app
app = FastAPI(
    title="GradeSense API",
    description="AI-powered marksheet extraction API with OCR and LLM capabilities",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def verify_api_key(x_api_key: Optional[str] = Header(None)):
    """Verify API key"""
    if not x_api_key:
        raise HTTPException(status_code=401, detail="API key required")
    
    valid_keys = settings.API_KEYS.split(',')
    if x_api_key.strip() not in [key.strip() for key in valid_keys]:
        raise HTTPException(status_code=401, detail="Invalid API key")
    
    return x_api_key

@app.get("/", response_model=dict)
async def root():
    """Root endpoint"""
    return {
        "message": "GradeSense API - Railway Deployment",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/api/v1/health",
        "mode": "demo" if not FULL_FEATURES else "full"
    }

@app.get("/api/v1/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint"""
    try:
        if extraction_service:
            service_status = extraction_service.get_health_status()
        else:
            service_status = {"status": "initializing"}
            
        return HealthResponse(
            status="healthy",
            services=service_status,
            version="1.0.0",
            environment="railway" if not FULL_FEATURES else "full"
        )
    except Exception as e:
        logger.error(f"Health check error: {e}")
        return HealthResponse(
            status="unhealthy",
            services={"error": str(e)},
            version="1.0.0"
        )

@app.post("/api/v1/extract", response_model=ExtractionResponse)
async def extract_marksheet(
    file: UploadFile = File(...),
    api_key: str = Depends(verify_api_key)
):
    """Extract data from marksheet image or PDF"""
    try:
        # Validate file
        file_data = await file.read()
        validation = file_validator.validate_file(file, file_data)
        
        if not validation.is_valid:
            raise HTTPException(status_code=400, detail=validation.error)
        
        # Extract data
        if extraction_service:
            result = await extraction_service.extract_marksheet_data(file_data, file.filename)
            return ExtractionResponse(**result)
        else:
            raise HTTPException(status_code=503, detail="Extraction service not available")
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Extraction error: {e}")
        raise HTTPException(status_code=500, detail=f"Processing error: {str(e)}")

@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Global exception handler"""
    logger.error(f"Global error: {exc}")
    return JSONResponse(
        status_code=500,
        content={"detail": f"Internal server error: {str(exc)}"}
    )

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
