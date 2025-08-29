"""
Test file for the extraction service
"""

import pytest
import asyncio
from fastapi.testclient import TestClient
from unittest.mock import Mock, patch
import json
import io
from PIL import Image

from app.main import app
from app.services.extraction_service import ExtractionService
from app.models.response_models import ExtractedData

client = TestClient(app)

class TestExtractionAPI:
    """Test cases for the extraction API"""
    
    def test_health_check(self):
        """Test health check endpoint"""
        response = client.get("/api/v1/health")
        assert response.status_code == 200
        data = response.json()
        assert "status" in data
        assert "services" in data
    
    def test_root_endpoint(self):
        """Test root endpoint"""
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "version" in data
    
    def test_extract_without_api_key(self):
        """Test extraction without API key"""
        # Create a dummy image file
        img = Image.new('RGB', (100, 100), color='white')
        img_byte_arr = io.BytesIO()
        img.save(img_byte_arr, format='PNG')
        img_byte_arr.seek(0)
        
        response = client.post(
            "/api/v1/extract",
            files={"file": ("test.png", img_byte_arr, "image/png")}
        )
        assert response.status_code == 401
    
    def test_extract_with_invalid_file(self):
        """Test extraction with invalid file"""
        # Create a text file instead of image
        text_file = io.BytesIO(b"This is not an image")
        
        response = client.post(
            "/api/v1/extract",
            files={"file": ("test.txt", text_file, "text/plain")},
            headers={"Authorization": "Bearer test-key"}
        )
        assert response.status_code == 400
    
    @patch('app.services.extraction_service.ExtractionService.extract_marksheet_data')
    def test_extract_success(self, mock_extract):
        """Test successful extraction"""
        # Mock the extraction result
        mock_result = Mock()
        mock_result.data = self._create_mock_extracted_data()
        mock_result.model_used = "gemini-pro"
        mock_extract.return_value = mock_result
        
        # Create a dummy image file
        img = Image.new('RGB', (100, 100), color='white')
        img_byte_arr = io.BytesIO()
        img.save(img_byte_arr, format='PNG')
        img_byte_arr.seek(0)
        
        response = client.post(
            "/api/v1/extract",
            files={"file": ("test.png", img_byte_arr, "image/png")},
            headers={"Authorization": "Bearer test-key"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert "data" in data
        assert "processing_time" in data
        assert "model_used" in data
    
    def _create_mock_extracted_data(self):
        """Create mock extracted data for testing"""
        from app.models.response_models import (
            ExtractedData, CandidateDetails, OverallResult, 
            DocumentInfo, FieldWithConfidence
        )
        
        candidate_details = CandidateDetails(
            name=FieldWithConfidence(value="John Doe", confidence=0.95),
            roll_no=FieldWithConfidence(value="12345", confidence=0.98)
        )
        
        return ExtractedData(
            candidate_details=candidate_details,
            subjects=[],
            overall_result=OverallResult(),
            document_info=DocumentInfo()
        )

class TestExtractionService:
    """Test cases for the extraction service"""
    
    @pytest.fixture
    def extraction_service(self):
        """Create extraction service instance"""
        return ExtractionService()
    
    @patch('app.services.ocr_service.OCRService.extract_text')
    @patch('app.services.llm_service.LLMService.structure_marksheet_data')
    @patch('app.services.confidence_service.ConfidenceService.calculate_confidence_scores')
    async def test_extract_marksheet_data(
        self, 
        mock_confidence, 
        mock_llm, 
        mock_ocr,
        extraction_service
    ):
        """Test marksheet data extraction"""
        # Mock OCR result
        mock_ocr_result = Mock()
        mock_ocr_result.text = "Sample marksheet text"
        mock_ocr_result.word_confidences = {"Sample": 0.9, "marksheet": 0.8}
        mock_ocr.return_value = mock_ocr_result
        
        # Mock LLM result
        mock_llm.return_value = {
            "candidate_details": {
                "name": {"value": "John Doe", "confidence": 0.95}
            },
            "subjects": [],
            "overall_result": {},
            "document_info": {}
        }
        
        # Mock confidence calculation
        mock_confidence.return_value = mock_llm.return_value
        
        # Create mock file
        mock_file = Mock()
        mock_file.filename = "test.png"
        mock_file.read = Mock(return_value=b"fake image data")
        mock_file.seek = Mock()
        
        # Test extraction
        result = await extraction_service.extract_marksheet_data(mock_file)
        
        assert result is not None
        assert result.model_used is not None
        
        # Verify mocks were called
        mock_ocr.assert_called_once()
        mock_llm.assert_called_once()
        mock_confidence.assert_called_once()

if __name__ == "__main__":
    pytest.main([__file__])
