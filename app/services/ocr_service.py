"""
OCR service for text extraction from images and PDFs
"""

# Optional imports for Railway compatibility
try:
    import pytesseract
    import cv2
    import numpy as np
    import fitz  # PyMuPDF
    HAS_OCR = True
except ImportError:
    HAS_OCR = False
    pytesseract = None
    cv2 = None
    np = None
    fitz = None

from PIL import Image
import io
import logging
from typing import Dict, List, Tuple, NamedTuple
from dataclasses import dataclass

from app.core.config import settings

logger = logging.getLogger(__name__)

@dataclass
class OCRResult:
    """Result container for OCR operations"""
    text: str
    word_confidences: Dict[str, float]
    bounding_boxes: List[Tuple[int, int, int, int]]  # (x, y, width, height)

class OCRService:
    """Service for extracting text from images and PDFs using Tesseract OCR"""
    
    def __init__(self):
        # Configure Tesseract path if specified
        if settings.TESSERACT_PATH and settings.TESSERACT_PATH != "tesseract":
            pytesseract.pytesseract.tesseract_cmd = settings.TESSERACT_PATH
            
    async def extract_text(self, file_content: bytes, file_extension: str) -> OCRResult:
        """
        Extract text from file content
        
        Args:
            file_content: Raw file bytes
            file_extension: File extension (jpg, png, pdf)
            
        Returns:
            OCRResult: Extracted text with confidence scores
        """
        try:
            if file_extension.lower() == 'pdf':
                return await self._extract_from_pdf(file_content)
            else:
                return await self._extract_from_image(file_content)
                
        except Exception as e:
            logger.error(f"OCR extraction failed: {e}")
            raise ValueError(f"OCR processing failed: {str(e)}")
    
    async def _extract_from_pdf(self, pdf_content: bytes) -> OCRResult:
        """Extract text from PDF file"""
        try:
            # Open PDF from bytes
            pdf_document = fitz.open(stream=pdf_content, filetype="pdf")
            
            all_text = []
            all_confidences = {}
            all_boxes = []
            
            for page_num in range(len(pdf_document)):
                page = pdf_document.load_page(page_num)
                
                # Try to extract text directly first
                page_text = page.get_text()
                
                if page_text.strip():
                    # If text is extractable, use it with high confidence
                    all_text.append(page_text)
                    words = page_text.split()
                    for word in words:
                        all_confidences[word] = 0.95  # High confidence for extractable text
                else:
                    # Convert page to image for OCR
                    pix = page.get_pixmap(matrix=fitz.Matrix(2, 2))  # 2x scale for better quality
                    img_data = pix.tobytes("png")
                    
                    # Process with OCR
                    ocr_result = await self._extract_from_image(img_data)
                    all_text.append(ocr_result.text)
                    all_confidences.update(ocr_result.word_confidences)
                    all_boxes.extend(ocr_result.bounding_boxes)
            
            pdf_document.close()
            
            return OCRResult(
                text="\n".join(all_text),
                word_confidences=all_confidences,
                bounding_boxes=all_boxes
            )
            
        except Exception as e:
            logger.error(f"PDF OCR failed: {e}")
            raise
    
    async def _extract_from_image(self, image_content: bytes) -> OCRResult:
        """Extract text from image file"""
        try:
            # Load image
            image = Image.open(io.BytesIO(image_content))
            
            # Convert to RGB if necessary
            if image.mode != 'RGB':
                image = image.convert('RGB')
            
            # Preprocess image if enabled
            if settings.ENABLE_PREPROCESSING:
                image = self._preprocess_image(image)
            
            # Extract text with detailed information
            custom_config = settings.OCR_CONFIG
            
            # Get detailed OCR data
            ocr_data = pytesseract.image_to_data(
                image, 
                config=custom_config,
                output_type=pytesseract.Output.DICT
            )
            
            # Extract text
            text = pytesseract.image_to_string(image, config=custom_config)
            
            # Process OCR data for confidence scores and bounding boxes
            word_confidences = {}
            bounding_boxes = []
            
            for i in range(len(ocr_data['text'])):
                word = ocr_data['text'][i].strip()
                conf = int(ocr_data['conf'][i])
                
                if word and conf > 0:  # Only process valid words with confidence
                    # Normalize confidence to 0-1 range
                    normalized_conf = min(conf / 100.0, 1.0)
                    word_confidences[word] = normalized_conf
                    
                    # Extract bounding box
                    x = ocr_data['left'][i]
                    y = ocr_data['top'][i]
                    w = ocr_data['width'][i]
                    h = ocr_data['height'][i]
                    bounding_boxes.append((x, y, w, h))
            
            return OCRResult(
                text=text,
                word_confidences=word_confidences,
                bounding_boxes=bounding_boxes
            )
            
        except Exception as e:
            logger.error(f"Image OCR failed: {e}")
            raise
    
    def _preprocess_image(self, image: Image.Image) -> Image.Image:
        """
        Preprocess image to improve OCR accuracy
        
        Args:
            image: PIL Image
            
        Returns:
            Image: Preprocessed image
        """
        try:
            # Convert PIL to OpenCV format
            cv_image = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
            
            # Convert to grayscale
            gray = cv2.cvtColor(cv_image, cv2.COLOR_BGR2GRAY)
            
            # Apply noise reduction
            denoised = cv2.medianBlur(gray, 3)
            
            # Apply adaptive thresholding
            thresh = cv2.adaptiveThreshold(
                denoised, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
                cv2.THRESH_BINARY, 11, 2
            )
            
            # Morphological operations to clean up
            kernel = np.ones((1, 1), np.uint8)
            cleaned = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel)
            
            # Convert back to PIL
            processed_image = Image.fromarray(cleaned)
            
            return processed_image
            
        except Exception as e:
            logger.warning(f"Image preprocessing failed, using original: {e}")
            return image
    
    def health_check(self) -> bool:
        """
        Check if OCR service is healthy
        
        Returns:
            bool: True if Tesseract is accessible
        """
        try:
            # Test Tesseract installation
            version = pytesseract.get_tesseract_version()
            logger.info(f"Tesseract version: {version}")
            return True
            
        except Exception as e:
            logger.error(f"Tesseract health check failed: {e}")
            return False
