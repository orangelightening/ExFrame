"""
Database setup and connection management for BrainUse.
"""

import os
import logging
from typing import Optional
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.ext.declarative import declarative_base

logger = logging.getLogger("tao.vetting.database")

# Base class for SQLAlchemy models
Base = declarative_base()

# Database connection
_engine = None
_SessionLocal = None


def get_database_url() -> str:
    """
    Get database URL from environment or use default.

    Returns:
        Database connection URL
    """
    # Check for PostgreSQL connection info
    host = os.getenv("POSTGRES_HOST", "localhost")
    port = os.getenv("POSTGRES_PORT", "5432")
    database = os.getenv("POSTGRES_DB", "brainuse")
    user = os.getenv("POSTGRES_USER", "brainuse")
    password = os.getenv("POSTGRES_PASSWORD", "brainuse")

    return f"postgresql://{user}:{password}@{host}:{port}/{database}"


def init_database(database_url: Optional[str] = None):
    """
    Initialize database connection.

    Args:
        database_url: Optional database URL (uses env vars if not provided)
    """
    global _engine, _SessionLocal

    if _engine is not None:
        logger.info("Database already initialized")
        return

    url = database_url or get_database_url()

    try:
        _engine = create_engine(
            url,
            pool_pre_ping=True,  # Verify connections before using
            pool_size=5,
            max_overflow=10
        )

        _SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=_engine)

        logger.info(f"Database initialized: {url.split('@')[1]}")  # Log without password

    except Exception as e:
        logger.error(f"Failed to initialize database: {e}")
        raise


def create_tables():
    """
    Create all database tables.

    Must be called after all models are imported.
    """
    if _engine is None:
        raise RuntimeError("Database not initialized. Call init_database() first.")

    # Import models to register them with Base
    from . import db_models

    Base.metadata.create_all(bind=_engine)
    logger.info("Database tables created")


def get_db() -> Session:
    """
    Get database session.

    Usage:
        db = get_db()
        try:
            # Use db
            db.commit()
        except:
            db.rollback()
            raise
        finally:
            db.close()

    Returns:
        SQLAlchemy Session
    """
    if _SessionLocal is None:
        raise RuntimeError("Database not initialized. Call init_database() first.")

    return _SessionLocal()


def close_database():
    """Close database connection."""
    global _engine, _SessionLocal

    if _engine is not None:
        _engine.dispose()
        _engine = None
        _SessionLocal = None
        logger.info("Database connection closed")
