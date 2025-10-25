"""
Database configuration and connection management.
Uses mock database for testing without PostgreSQL.
"""

import structlog
from typing import AsyncGenerator, Any
from app.core.config import settings
from app.core.mock_database import mock_db

logger = structlog.get_logger()

# Mock database instance
db = mock_db


async def get_db() -> AsyncGenerator[Any, None]:
    """Dependency to get mock database."""
    try:
        yield db
    except Exception as e:
        logger.error("Mock database error", error=str(e))
        raise


async def init_db() -> None:
    """Initialize mock database with sample data."""
    try:
        logger.info("Mock database initialized with sample data")
        logger.info(f"Sample data loaded: {len(mock_db.data['transactions'])} transactions, "
                   f"{len(mock_db.data['issuers'])} issuers, "
                   f"{len(mock_db.data['reconciliations'])} reconciliations")
    except Exception as e:
        logger.error("Failed to initialize mock database", error=str(e))
        raise
