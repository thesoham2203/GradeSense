"""
Image preprocessing utilities for better OCR results
"""

import cv2
import numpy as np
from PIL import Image, ImageEnhance, ImageFilter
from PIL.Image import Resampling
import logging

logger = logging.getLogger(__name__)

class ImagePreprocessor:
    """Image preprocessing for enhanced OCR accuracy"""
    
    def __init__(self):
        self.preprocessing_steps = [
            'convert_to_grayscale',
            'enhance_contrast',
            'reduce_noise',
            'correct_skew',
            'apply_threshold'
        ]
    
    def preprocess_image(self, image: Image.Image) -> Image.Image:
        """
        Apply preprocessing pipeline to improve OCR accuracy
        
        Args:
            image: PIL Image object
            
        Returns:
            Image: Preprocessed image
        """
        try:
            logger.info("Starting image preprocessing")
            
            # Convert to RGB if necessary
            if image.mode != 'RGB':
                image = image.convert('RGB')
            
            # Convert to OpenCV format
            cv_image = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
            
            # Apply preprocessing steps
            cv_image = self._convert_to_grayscale(cv_image)
            cv_image = self._enhance_contrast(cv_image)
            cv_image = self._reduce_noise(cv_image)
            cv_image = self._correct_skew(cv_image)
            cv_image = self._apply_threshold(cv_image)
            
            # Convert back to PIL
            if len(cv_image.shape) == 3:
                processed_image = Image.fromarray(cv2.cvtColor(cv_image, cv2.COLOR_BGR2RGB))
            else:
                processed_image = Image.fromarray(cv_image)
            
            logger.info("Image preprocessing completed")
            return processed_image
            
        except Exception as e:
            logger.error(f"Image preprocessing failed: {e}")
            return image  # Return original if preprocessing fails
    
    def _convert_to_grayscale(self, image: np.ndarray) -> np.ndarray:
        """Convert image to grayscale"""
        if len(image.shape) == 3:
            return cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        return image
    
    def _enhance_contrast(self, image: np.ndarray) -> np.ndarray:
        """Enhance image contrast using CLAHE"""
        try:
            # Apply CLAHE (Contrast Limited Adaptive Histogram Equalization)
            clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
            enhanced = clahe.apply(image)
            return enhanced
        except Exception as e:
            logger.warning(f"Contrast enhancement failed: {e}")
            return image
    
    def _reduce_noise(self, image: np.ndarray) -> np.ndarray:
        """Reduce noise using bilateral filter"""
        try:
            # Apply bilateral filter to reduce noise while preserving edges
            denoised = cv2.bilateralFilter(image, 9, 75, 75)
            return denoised
        except Exception as e:
            logger.warning(f"Noise reduction failed: {e}")
            return image
    
    def _correct_skew(self, image: np.ndarray) -> np.ndarray:
        """Correct skew in the image"""
        try:
            # Find text lines to determine skew angle
            coords = np.column_stack(np.where(image > 0))
            if len(coords) == 0:
                return image
            
            # Calculate skew angle using minimum area rectangle
            rect = cv2.minAreaRect(coords)
            angle = rect[2]
            
            # Correct angle calculation
            if angle < -45:
                angle = -(90 + angle)
            else:
                angle = -angle
            
            # Only correct if angle is significant (> 0.5 degrees)
            if abs(angle) > 0.5:
                # Get image center and rotation matrix
                (h, w) = image.shape[:2]
                center = (w // 2, h // 2)
                M = cv2.getRotationMatrix2D(center, angle, 1.0)
                
                # Apply rotation
                rotated = cv2.warpAffine(image, M, (w, h), 
                                       flags=cv2.INTER_CUBIC, 
                                       borderMode=cv2.BORDER_REPLICATE)
                return rotated
            
            return image
            
        except Exception as e:
            logger.warning(f"Skew correction failed: {e}")
            return image
    
    def _apply_threshold(self, image: np.ndarray) -> np.ndarray:
        """Apply adaptive thresholding"""
        try:
            # Apply adaptive threshold
            thresh = cv2.adaptiveThreshold(
                image, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
                cv2.THRESH_BINARY, 11, 2
            )
            
            # Apply morphological operations to clean up
            kernel = np.ones((1, 1), np.uint8)
            cleaned = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel)
            
            return cleaned
            
        except Exception as e:
            logger.warning(f"Thresholding failed: {e}")
            return image
    
    def enhance_for_ocr(self, image: Image.Image) -> Image.Image:
        """
        Apply OCR-specific enhancements
        
        Args:
            image: PIL Image object
            
        Returns:
            Image: Enhanced image optimized for OCR
        """
        try:
            # Resize image if too small (OCR works better on larger images)
            width, height = image.size
            if width < 1000 or height < 1000:
                scale_factor = max(1000 / width, 1000 / height)
                new_width = int(width * scale_factor)
                new_height = int(height * scale_factor)
                image = image.resize((new_width, new_height), Resampling.LANCZOS)
            
            # Enhance sharpness
            enhancer = ImageEnhance.Sharpness(image)
            image = enhancer.enhance(1.2)
            
            # Enhance contrast
            enhancer = ImageEnhance.Contrast(image)
            image = enhancer.enhance(1.1)
            
            return image
            
        except Exception as e:
            logger.warning(f"OCR enhancement failed: {e}")
            return image
    
    def preprocess_for_table_detection(self, image: Image.Image) -> Image.Image:
        """
        Preprocess image specifically for table/structure detection
        
        Args:
            image: PIL Image object
            
        Returns:
            Image: Preprocessed image optimized for table detection
        """
        try:
            # Convert to OpenCV
            cv_image = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
            
            # Convert to grayscale
            gray = cv2.cvtColor(cv_image, cv2.COLOR_BGR2GRAY)
            
            # Apply threshold to get binary image
            _, binary = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
            
            # Detect horizontal and vertical lines
            horizontal_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (25, 1))
            vertical_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (1, 25))
            
            # Extract horizontal and vertical lines
            horizontal_lines = cv2.morphologyEx(binary, cv2.MORPH_OPEN, horizontal_kernel)
            vertical_lines = cv2.morphologyEx(binary, cv2.MORPH_OPEN, vertical_kernel)
            
            # Combine lines
            lines = cv2.addWeighted(horizontal_lines, 0.5, vertical_lines, 0.5, 0.0)
            
            # Add lines back to original image
            result = cv2.addWeighted(binary, 0.8, lines, 0.2, 0.0)
            
            # Convert back to PIL
            return Image.fromarray(result)
            
        except Exception as e:
            logger.warning(f"Table preprocessing failed: {e}")
            return image
