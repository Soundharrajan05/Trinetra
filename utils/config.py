"""
Configuration management for TRINETRA AI system.
Loads environment variables from .env file and provides typed access.
"""

import os
from typing import Optional
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Config:
    """Configuration class for TRINETRA AI system."""
    
    # AI/ML Configuration
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")
    
    # Application Configuration
    API_HOST: str = os.getenv("API_HOST", "localhost")
    API_PORT: int = int(os.getenv("API_PORT", "8000"))
    API_DEBUG: bool = os.getenv("API_DEBUG", "true").lower() == "true"
    
    DASHBOARD_HOST: str = os.getenv("DASHBOARD_HOST", "localhost")
    DASHBOARD_PORT: int = int(os.getenv("DASHBOARD_PORT", "8501"))
    
    # Data Configuration
    DATASET_PATH: str = os.getenv("DATASET_PATH", "data/trinetra_trade_fraud_dataset_1000_rows_complex.csv")
    MODEL_PATH: str = os.getenv("MODEL_PATH", "models/isolation_forest.pkl")
    
    # ML Model Configuration
    CONTAMINATION_RATE: float = float(os.getenv("CONTAMINATION_RATE", "0.1"))
    N_ESTIMATORS: int = int(os.getenv("N_ESTIMATORS", "100"))
    RANDOM_STATE: int = int(os.getenv("RANDOM_STATE", "42"))
    
    # Risk Classification Thresholds
    SAFE_THRESHOLD: float = float(os.getenv("SAFE_THRESHOLD", "-0.2"))
    FRAUD_THRESHOLD: float = float(os.getenv("FRAUD_THRESHOLD", "0.2"))
    
    # Alert System Configuration
    PRICE_DEVIATION_THRESHOLD: float = float(os.getenv("PRICE_DEVIATION_THRESHOLD", "0.5"))
    COMPANY_RISK_THRESHOLD: float = float(os.getenv("COMPANY_RISK_THRESHOLD", "0.8"))
    PORT_ACTIVITY_THRESHOLD: float = float(os.getenv("PORT_ACTIVITY_THRESHOLD", "1.5"))
    
    # API Configuration
    GEMINI_MODEL: str = os.getenv("GEMINI_MODEL", "models/gemini-2.5-flash")
    GEMINI_TIMEOUT: int = int(os.getenv("GEMINI_TIMEOUT", "10"))
    GEMINI_MAX_RETRIES: int = int(os.getenv("GEMINI_MAX_RETRIES", "3"))
    
    # Logging Configuration
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    LOG_FILE: str = os.getenv("LOG_FILE", "trinetra.log")
    
    # Security Configuration
    CORS_ORIGINS: str = os.getenv("CORS_ORIGINS", "*")
    CORS_METHODS: str = os.getenv("CORS_METHODS", "*")
    CORS_HEADERS: str = os.getenv("CORS_HEADERS", "*")
    
    @classmethod
    def validate_required_config(cls) -> bool:
        """Validate that all required configuration is present."""
        if not cls.GEMINI_API_KEY:
            raise ValueError("GEMINI_API_KEY is required but not set in environment variables")
        
        if not os.path.exists(cls.DATASET_PATH):
            raise FileNotFoundError(f"Dataset file not found: {cls.DATASET_PATH}")
        
        return True
    
    @classmethod
    def get_cors_config(cls) -> dict:
        """Get CORS configuration as dictionary."""
        return {
            "allow_origins": cls.CORS_ORIGINS.split(",") if cls.CORS_ORIGINS != "*" else ["*"],
            "allow_methods": cls.CORS_METHODS.split(",") if cls.CORS_METHODS != "*" else ["*"],
            "allow_headers": cls.CORS_HEADERS.split(",") if cls.CORS_HEADERS != "*" else ["*"],
        }

# Create a global config instance
config = Config()