# GradeSense API - Technical Approach and Design Decisions

## Overview

GradeSense is an AI-powered marksheet extraction API that combines OCR technology with Large Language Models (LLMs) to extract structured data from educational documents with high accuracy and confidence scoring.

## Architecture Design

### 1. Microservices Architecture

The application follows a modular design with clear separation of concerns:

- **Main Application** (`app/main.py`): FastAPI application with routing and middleware
- **OCR Service** (`app/services/ocr_service.py`): Text extraction from images/PDFs
- **LLM Service** (`app/services/llm_service.py`): Intelligent data structuring
- **Confidence Service** (`app/services/confidence_service.py`): Multi-factor confidence scoring
- **Extraction Service** (`app/services/extraction_service.py`): Orchestration layer

### 2. Data Flow Pipeline

```
Input File → Validation → OCR → LLM Structuring → Confidence Calculation → JSON Output
```

## Extraction Approach

### 1. OCR (Optical Character Recognition)

- **Technology**: Tesseract OCR with OpenCV preprocessing
- **Preprocessing Pipeline**:
  - Grayscale conversion
  - Contrast enhancement (CLAHE)
  - Noise reduction (bilateral filtering)
  - Skew correction
  - Adaptive thresholding
- **Multi-format Support**: Images (JPG, PNG) and PDFs
- **PDF Handling**: Text extraction first, fallback to OCR for scanned PDFs

### 2. LLM-Powered Structuring

- **Supported Models**: Google Gemini Pro, OpenAI GPT-3.5/4
- **Structured Prompting**: Detailed prompts with JSON schema specification
- **Context-Aware**: Uses OCR confidence scores to guide extraction
- **Field Coverage**:
  - Candidate details (name, roll number, etc.)
  - Subject-wise marks and grades
  - Overall results and percentages
  - Document metadata

### 3. Multi-Factor Confidence Scoring

Our confidence scoring system uses a weighted combination of multiple factors:

#### Confidence Components:

1. **OCR Confidence (30%)**: Tesseract's character-level confidence
2. **Pattern Matching (20%)**: Regex validation for structured fields
3. **LLM Confidence (40%)**: Model's certainty in field classification
4. **Contextual Validation (10%)**: Cross-field consistency checks

#### Formula:

```
Final_Confidence = (OCR_Conf × 0.3) + (Pattern_Conf × 0.2) + (LLM_Conf × 0.4) + (Context_Conf × 0.1)
```

#### Field-Specific Validation:

- **Names**: Character pattern validation + OCR clarity
- **Numbers**: Numeric range validation + format checking
- **Dates**: Format validation + temporal consistency
- **Grades**: Standard grading pattern matching

## Design Decisions

### 1. Technology Choices

#### Why FastAPI?

- High performance async capabilities
- Automatic OpenAPI documentation
- Built-in validation with Pydantic
- Excellent type hinting support

#### Why Tesseract + LLM Combination?

- **Tesseract**: Reliable, open-source OCR with confidence scores
- **LLM**: Intelligent understanding of context and field relationships
- **Combined**: OCR provides raw text, LLM provides structure and meaning

#### LLM Provider Flexibility

- Configurable providers (Gemini/OpenAI)
- Environment-based switching
- Async implementation for better performance

### 2. Error Handling Strategy

- **Graceful Degradation**: Return partial results when possible
- **Comprehensive Validation**: File type, size, content validation
- **Detailed Error Messages**: Clear feedback for debugging
- **Logging**: Structured logging for monitoring and debugging

### 3. Security Considerations

- **API Key Authentication**: Multiple key support
- **File Size Limits**: Protection against DoS attacks
- **Content Validation**: MIME type verification
- **No Data Persistence**: Files processed in memory only

### 4. Performance Optimizations

- **Async Processing**: Non-blocking I/O operations
- **Batch Processing**: Multiple file handling
- **Image Preprocessing**: Conditional based on settings
- **Concurrent Requests**: FastAPI's built-in concurrency

## Confidence Calibration Method

### 1. OCR Confidence Integration

- Word-level confidence from Tesseract
- Average confidence calculation for multi-word fields
- Confidence normalization (0-100 → 0-1)

### 2. Pattern-Based Validation

```python
patterns = {
    'roll_number': [r'\b\d{4,12}\b', r'\b[A-Z]{1,3}\d{4,8}\b'],
    'date': [r'\b\d{1,2}[-/]\d{1,2}[-/]\d{4}\b'],
    'percentage': [r'\b\d{1,3}\.\d{1,2}%?\b']
}
```

### 3. Contextual Validation

- Cross-field consistency checks
- Calculated field verification (percentage from marks)
- Document type appropriate field presence

### 4. Confidence Thresholds

- Configurable minimum confidence threshold
- Field-specific confidence ranges:
  - Names: 0.8-0.95
  - Numbers: 0.9-0.98
  - Dates: 0.7-0.9
  - Grades: 0.85-0.95

## Scalability and Deployment

### 1. Docker Containerization

- Multi-stage builds for optimization
- System dependency management
- Health checks for monitoring

### 2. Cloud Deployment Ready

- Environment variable configuration
- Stateless design
- Horizontal scaling capability

### 3. Monitoring and Observability

- Structured logging
- Health check endpoints
- Processing time metrics
- Error tracking

## Innovation Features

### 1. Intelligent Preprocessing

- Automatic skew correction
- Adaptive thresholding
- Quality enhancement for better OCR

### 2. Multi-Modal Confidence

- Novel combination of OCR, pattern, and LLM confidence
- Weighted scoring based on field types
- Contextual validation

### 3. Flexible Architecture

- Pluggable LLM providers
- Configurable processing pipeline
- Extensible field definitions

### 4. Robust Error Handling

- Partial result extraction
- Fallback mechanisms
- Detailed error reporting

## Future Enhancements

1. **ML-Based Confidence Calibration**: Train models on confidence prediction
2. **Table Structure Recognition**: Advanced layout analysis
3. **Multi-Language Support**: Extended OCR language models
4. **Real-time Processing**: WebSocket-based streaming
5. **Blockchain Verification**: Document authenticity validation

## Testing Strategy

- **Unit Tests**: Individual component testing
- **Integration Tests**: End-to-end API testing
- **Mock Testing**: LLM and OCR service mocking
- **Sample Data**: Diverse marksheet formats

This approach ensures high accuracy, reliability, and scalability while maintaining flexibility for various marksheet formats and educational systems.
