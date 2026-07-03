from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from app.config import settings
from app.utils.logger import logger
import os

# Use file-based SQLite path
db_path = settings.DATABASE_URL.replace("sqlite:///./", "")

# Create engine
engine = create_engine(
    settings.DATABASE_URL,
    connect_args={"check_same_thread": False}
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def init_db():
    """Initialize database - creates all tables"""
    try:
        logger.info(f"Initializing database at {db_path}")
        
        # Drop all existing tables (development only!)
        Base.metadata.drop_all(bind=engine)
        logger.warning("⚠️  Dropped all existing tables")
        
        # Create all tables with new schema
        Base.metadata.create_all(bind=engine)
        logger.info("✓ Database initialized with new schema")
    except Exception as e:
        logger.error(f"Database initialization error: {str(e)}", exc_info=True)
        raise

def get_db():
    """Get database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()