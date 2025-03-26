# app/config.py
import os
from pydantic import BaseSettings
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Settings(BaseSettings):
    # Database settings
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL", 
        "postgresql://ashkan:password@dpg-cvhtllqqecs73d4r9a0-a:5432/hrv_records_db"
    )
    
    # API settings
    API_TITLE: str = "HRV Metrics API"
    API_VERSION: str = "1.0.0"
    API_DESCRIPTION: str = "API for Heart Rate Variability data analysis and processing"
    
    # CORS settings
    CORS_ORIGINS: list = ["*"]
    
    # App settings
    DEBUG: bool = os.getenv("DEBUG", "True").lower() == "true"
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

# Create settings instance
settings = Settings()