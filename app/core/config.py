"""
Configuration settings for the application
"""

import os
from typing import List
from pydantic_settings import BaseSettings
from pydantic import field_validator

class Settings(BaseSettings):
    # API Configuration
    API_TITLE: str = "GradeSense API"
    API_VERSION: str = "1.0.0"
    API_KEYS: str = "test-key,demo-key"  # Comma-separated API keys
    
    # File Upload Configuration
    MAX_FILE_SIZE: int = 10 * 1024 * 1024  # 10MB
    ALLOWED_EXTENSIONS: str = "jpg,jpeg,png,pdf"
    MAX_BATCH_SIZE: int = 10
    
    # LLM Configuration
    LLM_PROVIDER: str = "gemini"  # gemini or openai
    GEMINI_API_KEY: str = ""
    OPENAI_API_KEY: str = ""
    MODEL_TEMPERATURE: float = 0.1
    MAX_TOKENS: int = 4000
    
    # OCR Configuration  
    TESSERACT_PATH: str = "tesseract"  # Path to tesseract executable
    OCR_CONFIG: str = "--oem 3 --psm 6"  # Tesseract config
    
    # Processing Configuration
    CONFIDENCE_THRESHOLD: float = 0.5  # Minimum confidence for field acceptance
    ENABLE_PREPROCESSING: bool = True  # Image preprocessing
    
    # Logging
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    
    @field_validator('API_KEYS', mode='before')
    @classmethod
    def parse_api_keys(cls, v):
        if isinstance(v, str):
            return v  # Keep as string, will be parsed in property
        return v
    
    @field_validator('ALLOWED_EXTENSIONS', mode='before')
    @classmethod
    def parse_extensions(cls, v):
        if isinstance(v, str):
            return v  # Keep as string, will be parsed in property
        return v
    
    @property
    def get_api_keys(self) -> List[str]:
        if isinstance(self.API_KEYS, str):
            return [key.strip() for key in self.API_KEYS.split(',') if key.strip()]
        return self.API_KEYS
    
    @property
    def get_allowed_extensions(self) -> List[str]:
        if isinstance(self.ALLOWED_EXTENSIONS, str):
            return [ext.strip().lower() for ext in self.ALLOWED_EXTENSIONS.split(',') if ext.strip()]
        return self.ALLOWED_EXTENSIONS
    
    class Config:
        env_file = ".env"
        case_sensitive = True

# Global settings instance
settings = Settings()
