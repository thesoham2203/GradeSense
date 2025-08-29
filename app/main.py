"""
Main FastAPI application module for GradeSense API
"""

from fastapi import FastAPI, HTTPException, Depends, File, UploadFile, Security
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import time
import logging
from typing import List, Optional
import traceback

from app.core.config import settings
from app.core.security import verify_api_key
from app.services.extraction_service import ExtractionService
from app.models.response_models import (
    ExtractResponse, 
    ErrorResponse, 
    HealthResponse,
    BatchExtractResponse
)
from app.utils.file_validator import FileValidator
from app.utils.logger import setup_logger

# Setup logging
logger = setup_logger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="GradeSense API",
    description="AI-powered marksheet extraction API with confidence scoring",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize services
extraction_service = ExtractionService()
file_validator = FileValidator()

# Security
security = HTTPBearer(auto_error=False)

@app.middleware("http")
async def add_process_time_header(request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    return response

@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    logger.error(f"Global exception handler caught: {exc}")
    logger.error(traceback.format_exc())
    return JSONResponse(
        status_code=500,
        content={"status": "error", "message": "Internal server error", "detail": str(exc)}
    )

@app.get("/", response_model=dict)
async def root():
    """Root endpoint with API information"""
    return {
        "message": "Welcome to GradeSense API",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/api/v1/health"
    }

@app.get("/api/v1/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint"""
    try:
        # Test LLM service availability
        llm_status = await extraction_service.health_check()
        
        return HealthResponse(
            status="healthy",
            timestamp=time.time(),
            version="1.0.0",
            services={
                "llm": "healthy" if llm_status else "unhealthy",
                "ocr": "healthy"  # Tesseract is always available once installed
            }
        )
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return HealthResponse(
            status="unhealthy",
            timestamp=time.time(),
            version="1.0.0",
            services={
                "llm": "unhealthy",
                "ocr": "unknown"
            },
            error=str(e)
        )

@app.post("/api/v1/extract", response_model=ExtractResponse)
async def extract_marksheet(
    file: UploadFile = File(...),
    api_key: Optional[HTTPAuthorizationCredentials] = Security(security)
):
    """
    Extract structured data from a marksheet (image or PDF)
    
    - **file**: Marksheet file (JPG, PNG, PDF - max 10MB)
    - **X-API-Key**: Authentication header with API key
    
    Returns structured JSON with extracted fields and confidence scores
    """
    start_time = time.time()
    
    try:
        # Verify API key
        if not verify_api_key(api_key):
            raise HTTPException(status_code=401, detail="Invalid or missing API key")
        
        # Validate file
        validation_result = await file_validator.validate_file(file)
        if not validation_result.is_valid:
            raise HTTPException(
                status_code=400, 
                detail=f"File validation failed: {validation_result.error}"
            )
        
        logger.info(f"Processing file: {file.filename}, size: {file.size}")
        
        # Extract data
        extraction_result = await extraction_service.extract_marksheet_data(file)
        
        processing_time = time.time() - start_time
        
        return ExtractResponse(
            status="success",
            data=extraction_result.data,
            processing_time=processing_time,
            model_used=extraction_result.model_used,
            file_info={
                "filename": file.filename,
                "size": file.size,
                "content_type": file.content_type
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Extraction failed for {file.filename}: {e}")
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"Extraction failed: {str(e)}")

@app.post("/api/v1/extract/batch", response_model=BatchExtractResponse)
async def batch_extract_marksheets(
    files: List[UploadFile] = File(...),
    api_key: Optional[HTTPAuthorizationCredentials] = Security(security)
):
    """
    Extract structured data from multiple marksheets in batch
    
    - **files**: List of marksheet files (JPG, PNG, PDF - max 10MB each)
    - **X-API-Key**: Authentication header with API key
    
    Returns structured JSON array with extracted fields and confidence scores
    """
    start_time = time.time()
    
    try:
        # Verify API key
        if not verify_api_key(api_key):
            raise HTTPException(status_code=401, detail="Invalid or missing API key")
        
        if len(files) > settings.MAX_BATCH_SIZE:
            raise HTTPException(
                status_code=400, 
                detail=f"Too many files. Maximum {settings.MAX_BATCH_SIZE} files allowed"
            )
        
        results = []
        errors = []
        
        for file in files:
            try:
                # Validate each file
                validation_result = await file_validator.validate_file(file)
                if not validation_result.is_valid:
                    errors.append({
                        "filename": file.filename,
                        "error": validation_result.error
                    })
                    continue
                
                # Extract data
                extraction_result = await extraction_service.extract_marksheet_data(file)
                
                results.append({
                    "filename": file.filename,
                    "status": "success",
                    "data": extraction_result.data,
                    "model_used": extraction_result.model_used
                })
                
            except Exception as e:
                logger.error(f"Batch extraction failed for {file.filename}: {e}")
                errors.append({
                    "filename": file.filename,
                    "error": str(e)
                })
        
        processing_time = time.time() - start_time
        
        return BatchExtractResponse(
            status="completed",
            total_files=len(files),
            successful=len(results),
            failed=len(errors),
            results=results,
            errors=errors,
            processing_time=processing_time
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Batch extraction failed: {e}")
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"Batch extraction failed: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
