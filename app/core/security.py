"""
Security utilities for API key validation
"""

from typing import Optional
from fastapi.security import HTTPAuthorizationCredentials
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)

def verify_api_key(credentials: Optional[HTTPAuthorizationCredentials]) -> bool:
    """
    Verify API key from Authorization header
    
    Args:
        credentials: HTTP Authorization credentials
        
    Returns:
        bool: True if API key is valid, False otherwise
    """
    if not credentials:
        return False
    
    api_key = credentials.credentials
    valid_keys = settings.get_api_keys
    
    is_valid = api_key in valid_keys
    
    if not is_valid:
        logger.warning(f"Invalid API key attempted: {api_key[:8]}...")
    
    return is_valid

def get_api_key_from_header(api_key: str) -> bool:
    """
    Alternative method to verify API key directly from header
    
    Args:
        api_key: API key string
        
    Returns:
        bool: True if API key is valid, False otherwise
    """
    valid_keys = settings.get_api_keys
    return api_key in valid_keys
