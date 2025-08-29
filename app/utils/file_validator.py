"""
File validation utilities
"""

import logging
from typing import Optional, List
from fastapi import UploadFile
from dataclasses import dataclass

# Try to import magic, make it optional for Windows compatibility
try:
    import magic
    HAS_MAGIC = True
except ImportError:
    HAS_MAGIC = False
    magic = None

from app.core.config import settings

logger = logging.getLogger(__name__)

@dataclass
class ValidationResult:
    """Result of file validation"""
    is_valid: bool
    error: Optional[str] = None
    file_type: Optional[str] = None
    size: Optional[int] = None

class FileValidator:
    """Service for validating uploaded files"""
    
    def __init__(self):
        self.max_size = settings.MAX_FILE_SIZE
        self.allowed_extensions = settings.get_allowed_extensions
        
        # MIME types for allowed extensions
        self.allowed_mime_types = {
            'jpg': ['image/jpeg'],
            'jpeg': ['image/jpeg'],
            'png': ['image/png'],
            'pdf': ['application/pdf']
        }
    
    async def validate_file(self, file: UploadFile) -> ValidationResult:
        """
        Validate uploaded file
        
        Args:
            file: FastAPI UploadFile object
            
        Returns:
            ValidationResult: Validation result with details
        """
        try:
            # Check if file exists
            if not file or not file.filename:
                return ValidationResult(
                    is_valid=False,
                    error="No file provided"
                )
            
            # Check file size
            if hasattr(file, 'size') and file.size:
                if file.size > self.max_size:
                    return ValidationResult(
                        is_valid=False,
                        error=f"File size ({file.size} bytes) exceeds maximum allowed size ({self.max_size} bytes)",
                        size=file.size
                    )
            
            # Check file extension
            extension = self._get_file_extension(file.filename)
            if extension not in self.allowed_extensions:
                return ValidationResult(
                    is_valid=False,
                    error=f"File type '{extension}' not allowed. Allowed types: {', '.join(self.allowed_extensions)}"
                )
            
            # Read file content for MIME type validation
            file_content = await file.read()
            actual_size = len(file_content)
            
            # Reset file pointer
            await file.seek(0)
            
            # Check actual file size
            if actual_size > self.max_size:
                return ValidationResult(
                    is_valid=False,
                    error=f"File size ({actual_size} bytes) exceeds maximum allowed size ({self.max_size} bytes)",
                    size=actual_size
                )
            
            # Validate MIME type
            mime_validation = self._validate_mime_type(file_content, extension)
            if not mime_validation.is_valid:
                return mime_validation
            
            # Validate file content
            content_validation = self._validate_file_content(file_content, extension)
            if not content_validation.is_valid:
                return content_validation
            
            return ValidationResult(
                is_valid=True,
                file_type=extension,
                size=actual_size
            )
            
        except Exception as e:
            logger.error(f"File validation error: {e}")
            return ValidationResult(
                is_valid=False,
                error=f"Validation failed: {str(e)}"
            )
    
    def _get_file_extension(self, filename: str) -> str:
        """Extract file extension from filename"""
        if not filename or '.' not in filename:
            return ""
        return filename.split('.')[-1].lower()
    
    def _validate_mime_type(self, file_content: bytes, extension: str) -> ValidationResult:
        """
        Validate file MIME type matches extension
        
        Args:
            file_content: File content bytes
            extension: File extension
            
        Returns:
            ValidationResult: MIME type validation result
        """
        try:
            if not HAS_MAGIC or magic is None:
                # Skip MIME type validation if magic is not available
                logger.warning("python-magic not available, skipping MIME type validation")
                return ValidationResult(is_valid=True)
                
            # Use python-magic to detect MIME type
            mime_type = magic.from_buffer(file_content, mime=True)
            
            # Get allowed MIME types for extension
            allowed_mimes = self.allowed_mime_types.get(extension, [])
            
            if mime_type not in allowed_mimes:
                return ValidationResult(
                    is_valid=False,
                    error=f"File content type '{mime_type}' doesn't match extension '{extension}'"
                )
            
            return ValidationResult(is_valid=True, file_type=mime_type)
            
        except Exception as e:
            logger.warning(f"MIME type validation failed, skipping: {e}")
            # If MIME detection fails, allow file through with warning
            return ValidationResult(is_valid=True)
    
    def _validate_file_content(self, file_content: bytes, extension: str) -> ValidationResult:
        """
        Validate file content is not corrupted
        
        Args:
            file_content: File content bytes
            extension: File extension
            
        Returns:
            ValidationResult: Content validation result
        """
        try:
            if extension == 'pdf':
                return self._validate_pdf_content(file_content)
            elif extension in ['jpg', 'jpeg', 'png']:
                return self._validate_image_content(file_content)
            
            return ValidationResult(is_valid=True)
            
        except Exception as e:
            logger.error(f"Content validation error: {e}")
            return ValidationResult(
                is_valid=False,
                error=f"Content validation failed: {str(e)}"
            )
    
    def _validate_pdf_content(self, file_content: bytes) -> ValidationResult:
        """Validate PDF file content"""
        try:
            # Check PDF magic number
            if not file_content.startswith(b'%PDF'):
                return ValidationResult(
                    is_valid=False,
                    error="Invalid PDF file format"
                )
            
            # Check if file ends properly
            if b'%%EOF' not in file_content[-1024:]:
                logger.warning("PDF file might be truncated")
            
            return ValidationResult(is_valid=True)
            
        except Exception as e:
            return ValidationResult(
                is_valid=False,
                error=f"PDF validation failed: {str(e)}"
            )
    
    def _validate_image_content(self, file_content: bytes) -> ValidationResult:
        """Validate image file content"""
        try:
            from PIL import Image
            import io
            
            # Try to open image with PIL
            image = Image.open(io.BytesIO(file_content))
            
            # Verify image can be loaded
            image.verify()
            
            # Check image dimensions (reasonable limits)
            if image.size[0] > 10000 or image.size[1] > 10000:
                return ValidationResult(
                    is_valid=False,
                    error="Image dimensions too large (max 10000x10000)"
                )
            
            if image.size[0] < 50 or image.size[1] < 50:
                return ValidationResult(
                    is_valid=False,
                    error="Image dimensions too small (min 50x50)"
                )
            
            return ValidationResult(is_valid=True)
            
        except Exception as e:
            return ValidationResult(
                is_valid=False,
                error=f"Image validation failed: {str(e)}"
            )
    
    def get_validation_summary(self) -> dict:
        """Get validation configuration summary"""
        return {
            "max_file_size_mb": self.max_size / (1024 * 1024),
            "allowed_extensions": self.allowed_extensions,
            "allowed_mime_types": self.allowed_mime_types
        }
