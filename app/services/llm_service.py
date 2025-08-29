"""
LLM service for structuring extracted text into JSON format
"""

import json
import logging
from typing import Dict, Any, Optional
import asyncio
import aiohttp
import openai
import google.generativeai as genai

from app.core.config import settings

logger = logging.getLogger(__name__)

class LLMService:
    """Service for structuring marksheet text using Large Language Models"""
    
    def __init__(self):
        self.provider = settings.LLM_PROVIDER.lower()
        self.model_name = ""
        
        # Initialize based on provider
        if self.provider == "openai":
            self._init_openai()
        elif self.provider == "gemini":
            self._init_gemini()
        else:
            raise ValueError(f"Unsupported LLM provider: {self.provider}")
    
    def _init_openai(self):
        """Initialize OpenAI client"""
        if not settings.OPENAI_API_KEY:
            raise ValueError("OpenAI API key not configured")
        
        openai.api_key = settings.OPENAI_API_KEY
        self.model_name = "gpt-3.5-turbo"
        logger.info("Initialized OpenAI LLM service")
    
    def _init_gemini(self):
        """Initialize Gemini client"""
        if not settings.GEMINI_API_KEY:
            raise ValueError("Gemini API key not configured")
        
        genai.configure(api_key=settings.GEMINI_API_KEY)
        self.model_name = "gemini-pro"
        self.model = genai.GenerativeModel('gemini-pro')
        logger.info("Initialized Gemini LLM service")
    
    async def structure_marksheet_data(
        self, 
        extracted_text: str, 
        word_confidences: Dict[str, float]
    ) -> Dict[str, Any]:
        """
        Structure extracted text into JSON format using LLM
        
        Args:
            extracted_text: Raw OCR text
            word_confidences: Word-level confidence scores from OCR
            
        Returns:
            Dict: Structured marksheet data
        """
        try:
            # Create prompt for LLM
            prompt = self._create_structuring_prompt(extracted_text, word_confidences)
            
            # Get response from LLM
            if self.provider == "openai":
                response = await self._query_openai(prompt)
            elif self.provider == "gemini":
                response = await self._query_gemini(prompt)
            else:
                raise ValueError(f"Unsupported provider: {self.provider}")
            
            # Parse and validate JSON response
            structured_data = self._parse_llm_response(response)
            
            return structured_data
            
        except Exception as e:
            logger.error(f"LLM structuring failed: {e}")
            raise
    
    def _create_structuring_prompt(
        self, 
        text: str, 
        word_confidences: Dict[str, float]
    ) -> str:
        """Create structured prompt for LLM"""
        
        prompt = f"""
You are an expert at extracting structured data from educational marksheets. 
Analyze the following OCR-extracted text and convert it into a structured JSON format.

IMPORTANT INSTRUCTIONS:
1. Extract ALL available information, even if confidence is low
2. For each field, provide a confidence score (0.0 to 1.0)
3. If a field is not found, set value to null and confidence to 0.0
4. Confidence should be based on text clarity, context, and OCR confidence
5. Be conservative with confidence scores - better to underestimate than overestimate

OCR EXTRACTED TEXT:
{text}

WORD CONFIDENCE SCORES (OCR level):
{json.dumps(word_confidences, indent=2)}

OUTPUT FORMAT (JSON):
{{
  "candidate_details": {{
    "name": {{"value": "Full Name", "confidence": 0.95}},
    "father_name": {{"value": "Father's Name", "confidence": 0.90}},
    "mother_name": {{"value": "Mother's Name", "confidence": 0.90}},
    "roll_no": {{"value": "Roll Number", "confidence": 0.98}},
    "registration_no": {{"value": "Registration Number", "confidence": 0.95}},
    "dob": {{"value": "YYYY-MM-DD", "confidence": 0.85}},
    "exam_year": {{"value": "Year", "confidence": 0.90}},
    "board_university": {{"value": "Board/University Name", "confidence": 0.92}},
    "institution": {{"value": "School/College Name", "confidence": 0.88}}
  }},
  "subjects": [
    {{
      "subject": {{"value": "Subject Name", "confidence": 0.95}},
      "max_marks": {{"value": 100, "confidence": 0.98}},
      "obtained_marks": {{"value": 85, "confidence": 0.96}},
      "max_credits": {{"value": 4, "confidence": 0.90}},
      "obtained_credits": {{"value": 3.5, "confidence": 0.88}},
      "grade": {{"value": "A", "confidence": 0.92}}
    }}
  ],
  "overall_result": {{
    "result": {{"value": "PASS/FAIL", "confidence": 0.98}},
    "grade": {{"value": "First Division/A+/etc", "confidence": 0.90}},
    "percentage": {{"value": 78.5, "confidence": 0.85}},
    "cgpa": {{"value": 8.5, "confidence": 0.80}},
    "total_marks": {{"value": 425, "confidence": 0.90}},
    "max_total_marks": {{"value": 500, "confidence": 0.95}}
  }},
  "document_info": {{
    "issue_date": {{"value": "YYYY-MM-DD", "confidence": 0.80}},
    "issue_place": {{"value": "Place Name", "confidence": 0.75}},
    "document_type": {{"value": "Marksheet/Certificate", "confidence": 0.90}},
    "serial_number": {{"value": "Serial Number", "confidence": 0.85}}
  }}
}}

CONFIDENCE CALCULATION GUIDELINES:
- OCR word confidence + pattern matching + contextual validation
- Names: 0.8-0.95 (based on OCR clarity)
- Numbers (marks, roll no): 0.9-0.98 (usually clearer)
- Dates: 0.7-0.9 (format dependent)
- Grades: 0.85-0.95 (standardized format)
- Calculated fields (percentage): 0.8-0.9

Extract the information and return ONLY the JSON response without any additional text or explanation.
"""
        
        return prompt
    
    async def _query_openai(self, prompt: str) -> str:
        """Query OpenAI GPT model"""
        try:
            response = await openai.ChatCompletion.acreate(
                model=self.model_name,
                messages=[
                    {"role": "system", "content": "You are an expert data extraction assistant."},
                    {"role": "user", "content": prompt}
                ],
                temperature=settings.MODEL_TEMPERATURE,
                max_tokens=settings.MAX_TOKENS
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            logger.error(f"OpenAI query failed: {e}")
            raise
    
    async def _query_gemini(self, prompt: str) -> str:
        """Query Google Gemini model"""
        try:
            # Gemini doesn't have async support in the current SDK
            # We'll use asyncio.to_thread to make it async
            response = await asyncio.to_thread(
                self.model.generate_content,
                prompt
            )
            
            return response.text.strip()
            
        except Exception as e:
            logger.error(f"Gemini query failed: {e}")
            raise
    
    def _parse_llm_response(self, response: str) -> Dict[str, Any]:
        """
        Parse and validate LLM JSON response
        
        Args:
            response: Raw LLM response
            
        Returns:
            Dict: Parsed and validated data
        """
        try:
            # Try to extract JSON from response
            json_start = response.find('{')
            json_end = response.rfind('}') + 1
            
            if json_start == -1 or json_end == 0:
                raise ValueError("No JSON found in LLM response")
            
            json_str = response[json_start:json_end]
            
            # Parse JSON
            data = json.loads(json_str)
            
            # Validate structure
            self._validate_structure(data)
            
            return data
            
        except json.JSONDecodeError as e:
            logger.error(f"JSON parsing failed: {e}")
            logger.error(f"Raw response: {response}")
            raise ValueError(f"Invalid JSON from LLM: {e}")
        
        except Exception as e:
            logger.error(f"Response parsing failed: {e}")
            raise
    
    def _validate_structure(self, data: Dict[str, Any]):
        """Validate that the data has required structure"""
        required_sections = ['candidate_details', 'subjects', 'overall_result', 'document_info']
        
        for section in required_sections:
            if section not in data:
                data[section] = {}
        
        # Ensure subjects is a list
        if not isinstance(data['subjects'], list):
            data['subjects'] = []
        
        # Validate confidence scores
        self._validate_confidence_scores(data)
    
    def _validate_confidence_scores(self, data: Dict[str, Any]):
        """Ensure all confidence scores are valid (0.0 to 1.0)"""
        def validate_recursive(obj):
            if isinstance(obj, dict):
                if 'confidence' in obj:
                    # Ensure confidence is between 0 and 1
                    conf = obj.get('confidence', 0.0)
                    if not isinstance(conf, (int, float)) or conf < 0 or conf > 1:
                        obj['confidence'] = 0.0
                else:
                    for value in obj.values():
                        validate_recursive(value)
            elif isinstance(obj, list):
                for item in obj:
                    validate_recursive(item)
        
        validate_recursive(data)
    
    async def health_check(self) -> bool:
        """
        Check if LLM service is healthy
        
        Returns:
            bool: True if service is accessible
        """
        try:
            if self.provider == "openai":
                # Simple test query
                await openai.ChatCompletion.acreate(
                    model=self.model_name,
                    messages=[{"role": "user", "content": "Test"}],
                    max_tokens=10
                )
            elif self.provider == "gemini":
                # Simple test query
                await asyncio.to_thread(
                    self.model.generate_content,
                    "Test"
                )
            
            return True
            
        except Exception as e:
            logger.error(f"LLM health check failed: {e}")
            return False
    
    def get_model_name(self) -> str:
        """Get the current model name"""
        return f"{self.provider}-{self.model_name}"
