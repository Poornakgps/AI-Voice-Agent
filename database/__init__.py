# database/__init__.py (updated version)
"""
Database package for the Voice AI Restaurant Agent.

This module initializes the database connection and provides utilities.
"""
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy.ext.declarative import declarative_base
from contextlib import contextmanager
from app.config import settings
import logging

logger = logging.getLogger(__name__)

# Create engine
engine = create_engine(
    settings.DATABASE_URL,
    echo=settings.DEBUG,
    connect_args={"check_same_thread": False} if settings.DATABASE_URL.startswith("sqlite") else {}
)

# Create session factory
session_factory = sessionmaker(bind=engine)
SessionLocal = scoped_session(session_factory)

# Initialize database
def init_db():
    """Initialize the database."""
    from database.schema import create_tables
    from database.mock_data import seed_database
    
    logger.info("Initializing database...")
    
    # Create tables
    create_tables(engine)
    
    # Check if data already exists
    session = SessionLocal()
    try:
        # Check if we already have menu categories
        from database.models import MenuCategory
        existing_categories = session.query(MenuCategory).first()
        
        # Only seed if no data exists
        if not existing_categories:
            seed_database(session)
            logger.info("Database initialized with seed data.")
        else:
            logger.info("Database already contains data, skipping seed operation.")
    except Exception as e:
        logger.error(f"Error initializing database: {str(e)}")
        session.rollback()
        raise
    finally:
        session.close()

# Get database session
def get_db():
    """
    Get database session.
    
    Yields:
        Session: Database session
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@contextmanager
def db_session():
    """
    Context manager for database sessions.
    
    Yields:
        Session: Database session
    """
    session = SessionLocal()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()

# Database dependency for FastAPI
def get_db_dependency():
    """
    FastAPI dependency for database sessions.
    
    Yields:
        Session: Database session
    """
    with db_session() as session:
        yield session