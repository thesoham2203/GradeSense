"""
Railway-compatible OCR service that gracefully handles missing dependencies
"""

import logging
from typing import Dict, Any, Optional
from PIL import Image
import io

logger = logging.getLogger(__name__)

class RailwayOCRService:
    """Simplified OCR service for Railway deployment"""
    
    def __init__(self):
        """Initialize with basic image processing only"""
        self.available = True
        logger.info("Railway OCR Service initialized (basic mode)")
    
    async def extract_text_from_image(self, image_data: bytes) -> Dict[str, Any]:
        """
        Basic text extraction (placeholder for Railway)
        Returns demo data until OCR dependencies are available
        """
        try:
            # Validate image
            image = Image.open(io.BytesIO(image_data))
            width, height = image.size
            
            # Return demo extracted data
            return {
                "text": "DEMO EXTRACTION: Railway deployment detected. Full OCR capabilities require tesseract installation. This is a demo response showing the API structure.",
                "confidence": 0.95,
                "image_info": {
                    "width": width,
                    "height": height,
                    "format": image.format,
                    "mode": image.mode
                },
                "processing_mode": "railway_demo"
            }
            
        except Exception as e:
            logger.error(f"Railway OCR error: {e}")
            return {
                "text": "",
                "confidence": 0.0,
                "error": f"Image processing error: {str(e)}",
                "processing_mode": "railway_demo"
            }
    
    async def extract_text_from_pdf(self, pdf_data: bytes) -> Dict[str, Any]:
        """
        Basic PDF text extraction (placeholder for Railway)
        """
        return {
            "text": "DEMO EXTRACTION: PDF processing detected. Full PDF OCR capabilities require PyMuPDF installation. This is a demo response.",
            "confidence": 0.90,
            "page_count": 1,
            "processing_mode": "railway_demo"
        }
    
    def get_health_status(self) -> Dict[str, Any]:
        """Get service health status"""
        return {
            "service": "railway_ocr",
            "status": "healthy",
            "mode": "demo",
            "message": "Railway deployment - demo mode active"
        }
