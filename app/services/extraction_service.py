"""
Main extraction service that orchestrates OCR and LLM processing
"""

import asyncio
import json
import logging
from typing import Dict, Any, Optional
from fastapi import UploadFile
import time

from app.core.config import settings
from app.services.ocr_service import OCRService
from app.services.llm_service import LLMService
from app.services.confidence_service import ConfidenceService
from app.models.response_models import ExtractionResult, ExtractedData
from app.utils.image_preprocessor import ImagePreprocessor

logger = logging.getLogger(__name__)

class ExtractionService:
    """Main service for extracting structured data from marksheets"""
    
    def __init__(self):
        self.ocr_service = OCRService()
        self.llm_service = LLMService()
        self.confidence_service = ConfidenceService()
        self.image_preprocessor = ImagePreprocessor()
        
    async def extract_marksheet_data(self, file: UploadFile) -> ExtractionResult:
        """
        Extract structured data from a marksheet file
        
        Args:
            file: Uploaded marksheet file
            
        Returns:
            ExtractionResult: Structured data with confidence scores
        """
        try:
            logger.info(f"Starting extraction for file: {file.filename}")
            
            # Read file content
            file_content = await file.read()
            
            # Get file extension safely
            if file.filename and '.' in file.filename:
                file_extension = file.filename.split('.')[-1].lower()
            else:
                raise ValueError("Unable to determine file type from filename")
            
            # Step 1: Extract text using OCR
            logger.info("Step 1: OCR text extraction")
            ocr_result = await self.ocr_service.extract_text(
                file_content, 
                file_extension
            )
            
            if not ocr_result.text.strip():
                raise ValueError("No text could be extracted from the document")
            
            logger.info(f"OCR extracted {len(ocr_result.text)} characters")
            
            # Step 2: Structure data using LLM
            logger.info("Step 2: LLM data structuring")
            structured_data = await self.llm_service.structure_marksheet_data(
                ocr_result.text,
                ocr_result.word_confidences
            )
            
            # Step 3: Calculate confidence scores
            logger.info("Step 3: Confidence calculation")
            enhanced_data = await self.confidence_service.calculate_confidence_scores(
                structured_data,
                ocr_result.word_confidences,
                ocr_result.text
            )
            
            # Step 4: Validate and normalize
            logger.info("Step 4: Data validation")
            validated_data = self._validate_extracted_data(enhanced_data)
            
            logger.info("Extraction completed successfully")
            
            return ExtractionResult(
                data=validated_data,
                model_used=self.llm_service.get_model_name(),
                confidence_scores=self._extract_confidence_summary(validated_data)
            )
            
        except Exception as e:
            logger.error(f"Extraction failed: {e}")
            raise
        finally:
            # Reset file pointer
            await file.seek(0)
    
    def _validate_extracted_data(self, data: Dict[str, Any]) -> ExtractedData:
        """
        Validate and convert extracted data to structured format
        
        Args:
            data: Raw extracted data dictionary
            
        Returns:
            ExtractedData: Validated structured data
        """
        try:
            # Convert dictionary to ExtractedData model
            # This will handle validation and type conversion
            return ExtractedData.parse_obj(data)
            
        except Exception as e:
            logger.error(f"Data validation failed: {e}")
            # Return minimal valid structure if validation fails
            return self._create_minimal_response(data)
    
    def _create_minimal_response(self, data: Dict[str, Any]) -> ExtractedData:
        """
        Create minimal valid response when full validation fails
        
        Args:
            data: Raw extracted data
            
        Returns:
            ExtractedData: Minimal valid structure
        """
        from app.models.response_models import (
            CandidateDetails, OverallResult, DocumentInfo, FieldWithConfidence
        )
        
        # Extract basic required fields with low confidence
        name = data.get('candidate_details', {}).get('name', {})
        roll_no = data.get('candidate_details', {}).get('roll_no', {})
        
        candidate_details = CandidateDetails(
            name=FieldWithConfidence(
                value=name.get('value', 'Unknown'),
                confidence=name.get('confidence', 0.1)
            ),
            roll_no=FieldWithConfidence(
                value=roll_no.get('value', 'Unknown'),
                confidence=roll_no.get('confidence', 0.1)
            )
        )
        
        return ExtractedData(
            candidate_details=candidate_details,
            subjects=[],
            overall_result=OverallResult(),
            document_info=DocumentInfo()
        )
    
    def _extract_confidence_summary(self, data: ExtractedData) -> Dict[str, float]:
        """
        Extract summary of confidence scores for logging/monitoring
        
        Args:
            data: Structured extracted data
            
        Returns:
            Dict: Summary of confidence scores
        """
        scores = {}
        
        # Candidate details confidence
        if data.candidate_details.name:
            scores['name'] = data.candidate_details.name.confidence
        if data.candidate_details.roll_no:
            scores['roll_no'] = data.candidate_details.roll_no.confidence
            
        # Subject confidence (average)
        if data.subjects:
            subject_confidences = [
                s.subject.confidence for s in data.subjects if s.subject
            ]
            if subject_confidences:
                scores['subjects_avg'] = sum(subject_confidences) / len(subject_confidences)
        
        # Overall result confidence
        if data.overall_result.result:
            scores['result'] = data.overall_result.result.confidence
            
        return scores
    
    async def health_check(self) -> bool:
        """
        Check if extraction service is healthy
        
        Returns:
            bool: True if healthy, False otherwise
        """
        try:
            # Test LLM service
            llm_healthy = await self.llm_service.health_check()
            
            # Test OCR service
            ocr_healthy = self.ocr_service.health_check()
            
            return llm_healthy and ocr_healthy
            
        except Exception as e:
            logger.error(f"Health check failed: {e}")
            return False
