import os
from typing import List
from dotenv import load_dotenv

load_dotenv()

class Settings:
    # API Configuration
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")
    
    # File Upload Settings
    MAX_FILE_SIZE: int = 50 * 1024 * 1024  # 50MB
    ALLOWED_FILE_TYPES: List[str] = [".docx"]
    UPLOAD_DIR: str = "uploads"
    OUTPUT_DIR: str = "outputs"
    
    # ChromaDB Settings
    CHROMA_DB_PATH: str = "data/chroma_db"
    ADGM_KNOWLEDGE_PATH: str = "data/adgm_knowledge"
    
    # Processing Settings
    MAX_CONCURRENT_ANALYSES: int = 5
    GEMINI_MODEL: str = "gemini-2.0-flash-exp"
    MAX_TOKENS_PER_REQUEST: int = 8000
    
    # ADGM Document Types
    ADGM_DOCUMENT_TYPES = {
        "memorandum": {
            "name": "Memorandum of Association",
            "required_sections": [
                "company_name", "registered_office", "objects", 
                "share_capital", "liability", "subscriber_details"
            ]
        },
        "articles": {
            "name": "Articles of Association", 
            "required_sections": [
                "share_classes", "directors_powers", "meetings",
                "dividend_policy", "transfer_restrictions"
            ]
        },
        "application": {
            "name": "Company Registration Application",
            "required_sections": [
                "company_details", "directors_info", "shareholders_info",
                "business_activities", "financial_projections"
            ]
        },
        "board_resolution": {
            "name": "Board Resolution",
            "required_sections": [
                "resolution_date", "attendees", "resolutions_passed",
                "authorization", "signatures"
            ]
        }
    }
    
    # Red Flag Patterns
    RED_FLAG_PATTERNS = [
        "unlawful activities",
        "money laundering",
        "terrorist financing", 
        "regulatory violations",
        "sanctions violations",
        "prohibited activities",
        "inadequate capital",
        "missing signatures",
        "incomplete information",
        "inconsistent dates",
        "unauthorized activities"
    ]

settings = Settings()