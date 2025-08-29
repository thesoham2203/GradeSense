"""
Minimal FastAPI app for Railway deployment
"""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import os
from typing import Dict, Any

# Create FastAPI app
app = FastAPI(
    title="GradeSense API",
    description="AI-powered marksheet extraction API",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root() -> Dict[str, Any]:
    """Root endpoint"""
    return {
        "message": "GradeSense API - Railway Deployment",
        "version": "1.0.0",
        "status": "running",
        "docs": "/docs",
        "health": "/api/v1/health"
    }

@app.get("/api/v1/health")
async def health_check() -> Dict[str, Any]:
    """Health check endpoint"""
    return {
        "status": "healthy",
        "version": "1.0.0",
        "environment": "railway",
        "port": os.getenv("PORT", "8000")
    }

@app.get("/docs-url")
async def get_docs_url() -> Dict[str, Any]:
    """Get the public docs URL"""
    base_url = os.getenv("RAILWAY_PUBLIC_DOMAIN", "localhost:8000")
    return {
        "docs_url": f"https://{base_url}/docs",
        "redoc_url": f"https://{base_url}/redoc",
        "api_url": f"https://{base_url}",
        "health_url": f"https://{base_url}/api/v1/health"
    }

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
