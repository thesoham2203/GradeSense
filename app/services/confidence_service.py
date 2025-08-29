"""
Confidence scoring service for extracted data validation
"""

import re
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime
import statistics

from app.core.config import settings

logger = logging.getLogger(__name__)

class ConfidenceService:
    """Service for calculating and validating confidence scores"""
    
    def __init__(self):
        # Pattern matching confidence weights
        self.pattern_weights = {
            'exact_match': 0.9,
            'partial_match': 0.7,
            'format_match': 0.8,
            'no_match': 0.1
        }
        
        # Define common patterns for validation
        self.patterns = {
            'roll_number': [
                r'\b\d{4,12}\b',  # 4-12 digit numbers
                r'\b[A-Z]{1,3}\d{4,8}\b',  # Letter prefix + numbers
                r'\b\d{2}[A-Z]{2}\d{4,6}\b'  # Mixed patterns
            ],
            'registration_number': [
                r'\b[A-Z]{2,4}\d{6,10}\b',
                r'\b\d{4,6}/\d{2,4}\b',
                r'\bREG\d{6,10}\b'
            ],
            'date': [
                r'\b\d{1,2}[-/]\d{1,2}[-/]\d{4}\b',  # DD/MM/YYYY or DD-MM-YYYY
                r'\b\d{4}[-/]\d{1,2}[-/]\d{1,2}\b',  # YYYY/MM/DD or YYYY-MM-DD
                r'\b\d{1,2}\s+[A-Za-z]{3,9}\s+\d{4}\b'  # DD Month YYYY
            ],
            'percentage': [
                r'\b\d{1,3}\.\d{1,2}%?\b',  # XX.XX% or XX.XX
                r'\b\d{1,3}%\b'  # XX%
            ],
            'grade': [
                r'\b[A-F][+-]?\b',  # A, B+, C-, etc.
                r'\bFirst\s+Division\b',
                r'\bSecond\s+Division\b',
                r'\bThird\s+Division\b',
                r'\bPass\b',
                r'\bFail\b'
            ],
            'marks': [
                r'\b\d{1,3}\s*/\s*\d{1,3}\b',  # XX/YY format
                r'\b\d{1,3}\b'  # Simple numbers
            ]
        }
    
    async def calculate_confidence_scores(
        self,
        structured_data: Dict[str, Any],
        ocr_confidences: Dict[str, float],
        original_text: str
    ) -> Dict[str, Any]:
        """
        Calculate enhanced confidence scores for extracted data
        
        Args:
            structured_data: LLM-structured data
            ocr_confidences: Word-level OCR confidence scores
            original_text: Original OCR text
            
        Returns:
            Dict: Enhanced data with recalculated confidence scores
        """
        try:
            logger.info("Calculating enhanced confidence scores")
            
            # Process each section
            enhanced_data = {}
            
            # Candidate details
            enhanced_data['candidate_details'] = await self._process_candidate_details(
                structured_data.get('candidate_details', {}),
                ocr_confidences,
                original_text
            )
            
            # Subjects
            enhanced_data['subjects'] = await self._process_subjects(
                structured_data.get('subjects', []),
                ocr_confidences,
                original_text
            )
            
            # Overall result
            enhanced_data['overall_result'] = await self._process_overall_result(
                structured_data.get('overall_result', {}),
                ocr_confidences,
                original_text
            )
            
            # Document info
            enhanced_data['document_info'] = await self._process_document_info(
                structured_data.get('document_info', {}),
                ocr_confidences,
                original_text
            )
            
            return enhanced_data
            
        except Exception as e:
            logger.error(f"Confidence calculation failed: {e}")
            # Return original data if calculation fails
            return structured_data
    
    async def _process_candidate_details(
        self,
        candidate_data: Dict[str, Any],
        ocr_confidences: Dict[str, float],
        original_text: str
    ) -> Dict[str, Any]:
        """Process candidate details with enhanced confidence"""
        
        processed = {}
        
        for field, data in candidate_data.items():
            if not isinstance(data, dict) or 'value' not in data:
                continue
                
            value = data['value']
            original_confidence = data.get('confidence', 0.5)
            
            # Calculate enhanced confidence based on field type
            if field in ['name', 'father_name', 'mother_name']:
                enhanced_conf = self._calculate_name_confidence(
                    value, original_confidence, ocr_confidences, original_text
                )
            elif field == 'roll_no':
                enhanced_conf = self._calculate_pattern_confidence(
                    value, 'roll_number', original_confidence, original_text
                )
            elif field == 'registration_no':
                enhanced_conf = self._calculate_pattern_confidence(
                    value, 'registration_number', original_confidence, original_text
                )
            elif field == 'dob':
                enhanced_conf = self._calculate_date_confidence(
                    value, original_confidence, original_text
                )
            else:
                enhanced_conf = self._calculate_text_confidence(
                    value, original_confidence, ocr_confidences, original_text
                )
            
            processed[field] = {
                'value': value,
                'confidence': min(enhanced_conf, 1.0)  # Cap at 1.0
            }
        
        return processed
    
    async def _process_subjects(
        self,
        subjects_data: List[Dict[str, Any]],
        ocr_confidences: Dict[str, float],
        original_text: str
    ) -> List[Dict[str, Any]]:
        """Process subjects with enhanced confidence"""
        
        processed_subjects = []
        
        for subject in subjects_data:
            processed_subject = {}
            
            for field, data in subject.items():
                if not isinstance(data, dict) or 'value' not in data:
                    continue
                    
                value = data['value']
                original_confidence = data.get('confidence', 0.5)
                
                if field in ['obtained_marks', 'max_marks']:
                    enhanced_conf = self._calculate_marks_confidence(
                        value, original_confidence, original_text
                    )
                elif field == 'grade':
                    enhanced_conf = self._calculate_pattern_confidence(
                        value, 'grade', original_confidence, original_text
                    )
                else:
                    enhanced_conf = self._calculate_text_confidence(
                        value, original_confidence, ocr_confidences, original_text
                    )
                
                processed_subject[field] = {
                    'value': value,
                    'confidence': min(enhanced_conf, 1.0)
                }
            
            processed_subjects.append(processed_subject)
        
        return processed_subjects
    
    async def _process_overall_result(
        self,
        result_data: Dict[str, Any],
        ocr_confidences: Dict[str, float],
        original_text: str
    ) -> Dict[str, Any]:
        """Process overall result with enhanced confidence"""
        
        processed = {}
        
        for field, data in result_data.items():
            if not isinstance(data, dict) or 'value' not in data:
                continue
                
            value = data['value']
            original_confidence = data.get('confidence', 0.5)
            
            if field == 'percentage':
                enhanced_conf = self._calculate_pattern_confidence(
                    value, 'percentage', original_confidence, original_text
                )
            elif field in ['result', 'grade']:
                enhanced_conf = self._calculate_pattern_confidence(
                    value, 'grade', original_confidence, original_text
                )
            elif field in ['total_marks', 'max_total_marks']:
                enhanced_conf = self._calculate_marks_confidence(
                    value, original_confidence, original_text
                )
            else:
                enhanced_conf = self._calculate_text_confidence(
                    value, original_confidence, ocr_confidences, original_text
                )
            
            processed[field] = {
                'value': value,
                'confidence': min(enhanced_conf, 1.0)
            }
        
        return processed
    
    async def _process_document_info(
        self,
        doc_data: Dict[str, Any],
        ocr_confidences: Dict[str, float],
        original_text: str
    ) -> Dict[str, Any]:
        """Process document info with enhanced confidence"""
        
        processed = {}
        
        for field, data in doc_data.items():
            if not isinstance(data, dict) or 'value' not in data:
                continue
                
            value = data['value']
            original_confidence = data.get('confidence', 0.5)
            
            if field == 'issue_date':
                enhanced_conf = self._calculate_date_confidence(
                    value, original_confidence, original_text
                )
            else:
                enhanced_conf = self._calculate_text_confidence(
                    value, original_confidence, ocr_confidences, original_text
                )
            
            processed[field] = {
                'value': value,
                'confidence': min(enhanced_conf, 1.0)
            }
        
        return processed
    
    def _calculate_name_confidence(
        self,
        value: str,
        original_confidence: float,
        ocr_confidences: Dict[str, float],
        original_text: str
    ) -> float:
        """Calculate confidence for name fields"""
        if not value or value == "Unknown":
            return 0.0
        
        # Base confidence from LLM
        base_conf = original_confidence
        
        # OCR word confidence
        words = value.split()
        word_confs = [ocr_confidences.get(word, 0.5) for word in words]
        avg_ocr_conf = statistics.mean(word_confs) if word_confs else 0.5
        
        # Text presence validation
        presence_conf = 1.0 if value.lower() in original_text.lower() else 0.3
        
        # Name pattern validation (basic)
        pattern_conf = 0.8 if re.match(r'^[A-Za-z\s\.]+$', value) else 0.4
        
        # Weighted combination
        final_conf = (
            base_conf * 0.4 +
            avg_ocr_conf * 0.3 +
            presence_conf * 0.2 +
            pattern_conf * 0.1
        )
        
        return final_conf
    
    def _calculate_pattern_confidence(
        self,
        value: str,
        pattern_type: str,
        original_confidence: float,
        original_text: str
    ) -> float:
        """Calculate confidence based on pattern matching"""
        if not value:
            return 0.0
        
        # Base confidence from LLM
        base_conf = original_confidence
        
        # Pattern matching
        patterns = self.patterns.get(pattern_type, [])
        pattern_conf = 0.1  # Default low confidence
        
        value_str = str(value)
        for pattern in patterns:
            if re.search(pattern, value_str, re.IGNORECASE):
                pattern_conf = 0.9
                break
        
        # Text presence validation
        presence_conf = 1.0 if value_str.lower() in original_text.lower() else 0.2
        
        # Weighted combination
        final_conf = (
            base_conf * 0.4 +
            pattern_conf * 0.4 +
            presence_conf * 0.2
        )
        
        return final_conf
    
    def _calculate_date_confidence(
        self,
        value: str,
        original_confidence: float,
        original_text: str
    ) -> float:
        """Calculate confidence for date fields"""
        if not value:
            return 0.0
        
        # Base confidence
        base_conf = original_confidence
        
        # Date format validation
        format_conf = 0.1
        try:
            # Try parsing different date formats
            for fmt in ['%Y-%m-%d', '%d/%m/%Y', '%d-%m-%Y', '%d %B %Y']:
                try:
                    datetime.strptime(value, fmt)
                    format_conf = 0.9
                    break
                except ValueError:
                    continue
        except:
            pass
        
        # Pattern matching
        pattern_conf = self._calculate_pattern_confidence(
            value, 'date', original_confidence, original_text
        )
        
        # Weighted combination
        final_conf = (
            base_conf * 0.3 +
            format_conf * 0.4 +
            pattern_conf * 0.3
        )
        
        return final_conf
    
    def _calculate_marks_confidence(
        self,
        value: Any,
        original_confidence: float,
        original_text: str
    ) -> float:
        """Calculate confidence for marks/numbers"""
        if value is None:
            return 0.0
        
        # Base confidence
        base_conf = original_confidence
        
        # Numeric validation
        numeric_conf = 0.1
        try:
            num_val = float(value)
            if 0 <= num_val <= 1000:  # Reasonable range for marks
                numeric_conf = 0.9
            elif num_val > 1000:
                numeric_conf = 0.5  # Could be valid but less likely
        except (ValueError, TypeError):
            pass
        
        # Text presence validation
        value_str = str(value)
        presence_conf = 1.0 if value_str in original_text else 0.3
        
        # Weighted combination
        final_conf = (
            base_conf * 0.4 +
            numeric_conf * 0.4 +
            presence_conf * 0.2
        )
        
        return final_conf
    
    def _calculate_text_confidence(
        self,
        value: str,
        original_confidence: float,
        ocr_confidences: Dict[str, float],
        original_text: str
    ) -> float:
        """Calculate confidence for general text fields"""
        if not value:
            return 0.0
        
        # Base confidence
        base_conf = original_confidence
        
        # OCR word confidence
        words = str(value).split()
        word_confs = [ocr_confidences.get(word, 0.5) for word in words]
        avg_ocr_conf = statistics.mean(word_confs) if word_confs else 0.5
        
        # Text presence validation
        presence_conf = 1.0 if value.lower() in original_text.lower() else 0.2
        
        # Weighted combination
        final_conf = (
            base_conf * 0.5 +
            avg_ocr_conf * 0.3 +
            presence_conf * 0.2
        )
        
        return final_conf
