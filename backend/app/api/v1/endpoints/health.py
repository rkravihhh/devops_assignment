"""
Health check endpoints.
"""

from fastapi import APIRouter, Depends
from app.core.database import get_db
from app.services.health_service import HealthService

router = APIRouter()


@router.get("/")
async def health_check() -> None:
    """Basic health check endpoint."""
    return {"status": "healthy", "service": "txn-reconcile-api"}


@router.get("/detailed")
async def detailed_health_check(db = Depends(get_db)):
    """Detailed health check including database connectivity."""
    health_service = HealthService(db)
    return await health_service.get_detailed_health()
