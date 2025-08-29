# GradeSense - AI-Powered Marksheet Extraction API

## Overview

GradeSense is an intelligent API that extracts structured data from marksheets (images and PDFs) using advanced LLM technology. It provides accurate field extraction with confidence scores for reliable data processing.

## Features

- 📄 Supports both PDF and image formats (JPG, PNG)
- 🧠 LLM-powered extraction with Gemini/OpenAI
- 📊 Confidence scoring for each extracted field
- 🚀 FastAPI-based high-performance API
- 🔄 Concurrent request handling
- 🛡️ Robust error handling and validation
- 🔑 API key authentication
- 📦 Batch processing support
- 🎯 Consistent JSON schema output

## Tech Stack

- **Backend**: Python 3.9+ with FastAPI
- **LLM**: Google Gemini / OpenAI GPT
- **OCR**: Tesseract with pytesseract
- **PDF Processing**: PyMuPDF (fitz)
- **Image Processing**: Pillow, OpenCV
- **Deployment**: Docker + Cloud platforms

## Installation

### Prerequisites

- Python 3.9+
- Tesseract OCR
- Git

### Setup

1. **Clone the repository**

```bash
git clone 
cd gradesense
```

2. **Create virtual environment**

```bash
python -m venv venv
# Windows
venv\Scripts\activate
# Linux/Mac
source venv/bin/activate
```

3. **Install dependencies**

```bash
pip install -r requirements.txt
```

4. **Install Tesseract OCR**

   - Windows: Download from [GitHub releases](https://github.com/UB-Mannheim/tesseract/wiki)
   - Ubuntu/Debian: `sudo apt-get install tesseract-ocr`
   - macOS: `brew install tesseract`

5. **Environment Configuration**

```bash
cp .env.example .env
# Edit .env with your API keys
```

6. **Run the application**

```bash
uvicorn app.main:app --reload
```

## API Documentation

### Base URL

```
http://localhost:8000
```

### Authentication

Include API key in headers:

```
X-API-Key: your-api-key-here
```

### Endpoints

#### 1. Extract Marksheet Data

```http
POST /api/v1/extract
Content-Type: multipart/form-data

Parameters:
- file: marksheet file (JPG/PNG/PDF, max 10MB)
```

**Response:**

```json
{
  "status": "success",
  "data": {
    "candidate_details": {
      "name": {
        "value": "John Doe",
        "confidence": 0.95
      },
      "father_name": {
        "value": "Robert Doe",
        "confidence": 0.92
      },
      "roll_no": {
        "value": "12345",
        "confidence": 0.98
      },
      "registration_no": {
        "value": "REG2023001",
        "confidence": 0.9
      },
      "dob": {
        "value": "1999-05-15",
        "confidence": 0.88
      },
      "exam_year": {
        "value": "2023",
        "confidence": 0.96
      },
      "board_university": {
        "value": "CBSE",
        "confidence": 0.94
      },
      "institution": {
        "value": "ABC School",
        "confidence": 0.89
      }
    },
    "subjects": [
      {
        "subject": {
          "value": "Mathematics",
          "confidence": 0.97
        },
        "max_marks": {
          "value": 100,
          "confidence": 0.99
        },
        "obtained_marks": {
          "value": 85,
          "confidence": 0.96
        },
        "grade": {
          "value": "A",
          "confidence": 0.93
        }
      }
    ],
    "overall_result": {
      "result": {
        "value": "PASS",
        "confidence": 0.98
      },
      "grade": {
        "value": "First Division",
        "confidence": 0.91
      },
      "percentage": {
        "value": 78.5,
        "confidence": 0.89
      }
    },
    "document_info": {
      "issue_date": {
        "value": "2023-06-15",
        "confidence": 0.85
      },
      "issue_place": {
        "value": "New Delhi",
        "confidence": 0.82
      }
    }
  },
  "processing_time": 2.34,
  "model_used": "gemini-pro"
}
```

#### 2. Batch Extract

```http
POST /api/v1/extract/batch
Content-Type: multipart/form-data

Parameters:
- files: multiple marksheet files
```

#### 3. Health Check

```http
GET /api/v1/health
```

## Configuration

### Environment Variables

```env
# LLM Configuration
GEMINI_API_KEY=your_gemini_api_key
OPENAI_API_KEY=your_openai_api_key
LLM_PROVIDER=gemini  # or openai

# API Configuration
API_KEYS=key1,key2,key3
MAX_FILE_SIZE=10485760  # 10MB
ALLOWED_EXTENSIONS=jpg,jpeg,png,pdf

# Tesseract Configuration
TESSERACT_PATH=/usr/bin/tesseract
```

## Confidence Scoring

Our confidence scoring system uses multiple factors:

1. **OCR Confidence**: Tesseract's character-level confidence
2. **Pattern Matching**: Regex pattern validation scores
3. **LLM Confidence**: Model's certainty in field classification
4. **Contextual Validation**: Cross-field consistency checks

**Formula:**

```
Final_Confidence = (OCR_Conf * 0.3) + (Pattern_Conf * 0.2) + (LLM_Conf * 0.4) + (Context_Conf * 0.1)
```

## Testing

### Unit Tests

```bash
pytest tests/ -v
```

### Test with Sample Files

```bash
# Test single file
curl -X POST "http://localhost:8000/api/v1/extract" \
  -H "X-API-Key: test-key" \
  -F "file=@test_samples/sample_marksheet.pdf"
```

## Docker Deployment

```bash
# Build image
docker build -t gradesense .

# Run container
docker run -p 8000:8000 --env-file .env gradesense
```

## Sample Files

Test marksheets are provided in the `test_samples/` directory for testing purposes.

## Error Handling

The API provides comprehensive error handling:

- Invalid file formats
- File size exceeding limits
- Corrupted files
- Missing API keys
- Rate limiting
- OCR processing failures

## Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Support

For support and questions:

- Create an issue on GitHub
- Email: support@gradesense.com

---

**Live API**: [https://gradesense-api.herokuapp.com](https://gradesense-api.herokuapp.com)
**Documentation**: [https://gradesense-api.herokuapp.com/docs](https://gradesense-api.herokuapp.com/docs)
