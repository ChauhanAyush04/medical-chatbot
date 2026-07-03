import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    """Application settings"""
    
    # API
    DEBUG: bool = os.getenv("DEBUG", "True") == "True"
    
    # Database (SQLite)
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./medical_chatbot.db")
    
    # LLM
    GROQ_API_KEY: str = os.getenv("GROQ_API_KEY", "")
    LLM_MODEL: str = "llama-3.3-70b-versatile"
    LLM_TEMPERATURE: float = 0.3
    LLM_MAX_TOKENS: int = 256
    
    # Vector Store
    FAISS_PATH: str = "vectorstores/db_faiss"
    EMBEDDING_MODEL: str = "sentence-transformers/all-MiniLM-L6-v2"
    
    # Retrieval
    TOP_K: int = 2

settings = Settings()