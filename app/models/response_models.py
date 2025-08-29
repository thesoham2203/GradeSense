"""
Pydantic models for API responses
"""

from typing import Dict, List, Optional, Any, Union
from pydantic import BaseModel, Field
from datetime import datetime

class FieldWithConfidence(BaseModel):
    """Model for extracted field with confidence score"""
    value: Union[str, int, float, None] = None
    confidence: float = Field(..., ge=0.0, le=1.0, description="Confidence score between 0 and 1")

class CandidateDetails(BaseModel):
    """Candidate personal information"""
    name: FieldWithConfidence
    father_name: Optional[FieldWithConfidence] = None
    mother_name: Optional[FieldWithConfidence] = None
    roll_no: FieldWithConfidence
    registration_no: Optional[FieldWithConfidence] = None
    dob: Optional[FieldWithConfidence] = None
    exam_year: Optional[FieldWithConfidence] = None
    board_university: Optional[FieldWithConfidence] = None
    institution: Optional[FieldWithConfidence] = None

class Subject(BaseModel):
    """Subject marks information"""
    subject: FieldWithConfidence
    max_marks: Optional[FieldWithConfidence] = None
    obtained_marks: FieldWithConfidence
    max_credits: Optional[FieldWithConfidence] = None
    obtained_credits: Optional[FieldWithConfidence] = None
    grade: Optional[FieldWithConfidence] = None

class OverallResult(BaseModel):
    """Overall result information"""
    result: Optional[FieldWithConfidence] = None  # PASS/FAIL
    grade: Optional[FieldWithConfidence] = None   # First Division, A+, etc.
    percentage: Optional[FieldWithConfidence] = None
    cgpa: Optional[FieldWithConfidence] = None
    total_marks: Optional[FieldWithConfidence] = None
    max_total_marks: Optional[FieldWithConfidence] = None

class DocumentInfo(BaseModel):
    """Document metadata"""
    issue_date: Optional[FieldWithConfidence] = None
    issue_place: Optional[FieldWithConfidence] = None
    document_type: Optional[FieldWithConfidence] = None
    serial_number: Optional[FieldWithConfidence] = None

class ExtractedData(BaseModel):
    """Complete extracted marksheet data"""
    candidate_details: CandidateDetails
    subjects: List[Subject]
    overall_result: OverallResult
    document_info: DocumentInfo

class FileInfo(BaseModel):
    """Uploaded file information"""
    filename: str
    size: int
    content_type: str

class ExtractResponse(BaseModel):
    """Response model for single extraction"""
    model_config = {"protected_namespaces": ()}
    
    status: str = "success"
    data: ExtractedData
    processing_time: float
    model_used: str
    file_info: FileInfo
    timestamp: float = Field(default_factory=lambda: datetime.now().timestamp())

class BatchResultItem(BaseModel):
    """Single item in batch processing result"""
    model_config = {"protected_namespaces": ()}
    
    filename: str
    status: str
    data: Optional[ExtractedData] = None
    model_used: Optional[str] = None

class BatchErrorItem(BaseModel):
    """Error item in batch processing"""
    filename: str
    error: str

class BatchExtractResponse(BaseModel):
    """Response model for batch extraction"""
    status: str = "completed"
    total_files: int
    successful: int
    failed: int
    results: List[BatchResultItem]
    errors: List[BatchErrorItem]
    processing_time: float
    timestamp: float = Field(default_factory=lambda: datetime.now().timestamp())

class ErrorResponse(BaseModel):
    """Error response model"""
    status: str = "error"
    message: str
    detail: Optional[str] = None
    timestamp: float = Field(default_factory=lambda: datetime.now().timestamp())

class HealthResponse(BaseModel):
    """Health check response"""
    status: str
    timestamp: float
    version: str
    services: Dict[str, str]
    error: Optional[str] = None

class ExtractionResult(BaseModel):
    """Internal model for extraction service result"""
    model_config = {"protected_namespaces": ()}
    
    data: ExtractedData
    model_used: str
    confidence_scores: Dict[str, float]
