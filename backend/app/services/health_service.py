"""
Health check service.
"""

from typing import Dict, Any
import structlog

logger = structlog.get_logger()


class HealthService:
    """Service for health check operations."""
    
    def __init__(self, db: Any) -> None:
        self.db = db
    
    async def get_detailed_health(self) -> Dict[str, Any]:
        """Get detailed health status including database connectivity."""
        health_status: Dict[str, Any] = {
            "status": "healthy",
            "service": "txn-reconcile-api",
            "checks": {}
        }
        
        # Check mock database connectivity
        try:
            # Test mock database by getting a simple count
            transaction_count = len(self.db.data["transactions"])
            health_status["checks"]["database"] = {
                "status": "healthy",
                "message": f"Mock database connection successful - {transaction_count} transactions available"
            }
        except Exception as e:
            health_status["status"] = "unhealthy"
            health_status["checks"]["database"] = {
                "status": "unhealthy",
                "message": f"Mock database connection failed: {str(e)}"
            }
            logger.error("Mock database health check failed", error=str(e))
        
        return health_status
