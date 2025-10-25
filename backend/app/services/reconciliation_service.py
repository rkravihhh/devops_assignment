"""
Reconciliation service for business logic.
"""

from typing import Optional
from datetime import datetime
from decimal import Decimal
import structlog
import uuid

from app.schemas.reconciliation import (
    ReconciliationCreate, 
    ReconciliationUpdate, 
    ReconciliationResponse, 
    ReconciliationListResponse,
    ReconciliationSearchRequest,
    ReconciliationStatsResponse
)
from app.core.exceptions import ReconciliationError

logger = structlog.get_logger()


class ReconciliationService:
    """Service for reconciliation operations."""
    
    def __init__(self, db) -> None:
        self.db = db
    
    async def create_reconciliation(self, reconciliation_data: ReconciliationCreate) -> ReconciliationResponse:
        """Create a new reconciliation."""
        try:
            # Convert Pydantic model to dict
            reconciliation_dict = reconciliation_data.model_dump()
            
            # Create reconciliation using mock database
            reconciliation = self.db.create_reconciliation(reconciliation_dict)
            
            # Parse JSON metadata if it's a string
            if isinstance(reconciliation.get("metadata"), str):
                import json
                try:
                    reconciliation["metadata"] = json.loads(reconciliation["metadata"])
                except json.JSONDecodeError:
                    reconciliation["metadata"] = {}

            logger.info("Reconciliation created", reconciliation_id=reconciliation["reconciliation_id"])
            return ReconciliationResponse(**reconciliation)
            
        except Exception as e:
            logger.error("Failed to create reconciliation", error=str(e))
            raise
    
    async def get_reconciliation_by_id(self, reconciliation_id: str) -> Optional[ReconciliationResponse]:
        """Get a reconciliation by ID."""
        try:
            reconciliation = self.db.get_reconciliation_by_id(reconciliation_id)
            
            if not reconciliation:
                return None
            
            # Parse JSON metadata if it's a string
            if isinstance(reconciliation.get("metadata"), str):
                import json
                try:
                    reconciliation["metadata"] = json.loads(reconciliation["metadata"])
                except json.JSONDecodeError:
                    reconciliation["metadata"] = {}
                
            return ReconciliationResponse(**reconciliation)
            
        except Exception as e:
            logger.error("Failed to get reconciliation", reconciliation_id=reconciliation_id, error=str(e))
            raise
    
    async def update_reconciliation(self, reconciliation_id: str, update_data: ReconciliationUpdate) -> Optional[ReconciliationResponse]:
        """Update a reconciliation."""
        try:
            # Convert Pydantic model to dict, excluding None values
            update_dict = {k: v for k, v in update_data.model_dump().items() if v is not None}
            
            reconciliation = self.db.update_reconciliation(reconciliation_id, update_dict)
            
            if not reconciliation:
                return None
            
            logger.info("Reconciliation updated", reconciliation_id=reconciliation_id)
            return ReconciliationResponse(**reconciliation)
            
        except Exception as e:
            logger.error("Failed to update reconciliation", reconciliation_id=reconciliation_id, error=str(e))
            raise
    
    async def delete_reconciliation(self, reconciliation_id: str) -> bool:
        """Delete a reconciliation."""
        try:
            success = self.db.delete_reconciliation(reconciliation_id)
            
            if success:
                logger.info("Reconciliation deleted", reconciliation_id=reconciliation_id)
            else:
                logger.warning("Reconciliation not found for deletion", reconciliation_id=reconciliation_id)
            
            return success
            
        except Exception as e:
            logger.error("Failed to delete reconciliation", reconciliation_id=reconciliation_id, error=str(e))
            raise
    
    async def search_reconciliations(self, search_request: ReconciliationSearchRequest) -> ReconciliationListResponse:
        """Search reconciliations with filters."""
        try:
            # Convert search request to filters dict
            filters = {
                "issuer_id": search_request.issuer_id,
                "status": search_request.status,
                "reconciliation_type": search_request.reconciliation_type,
                "is_successful": search_request.is_successful
            }
            
            # Get filtered results
            reconciliations = self.db.search_reconciliations(filters)
            
            # Apply pagination
            total = len(reconciliations)
            start_idx = (search_request.page - 1) * search_request.size
            end_idx = start_idx + search_request.size
            paginated_reconciliations = reconciliations[start_idx:end_idx]
            
            # Convert to response objects, parsing JSON metadata
            reconciliation_responses = []
            for r in paginated_reconciliations:
                # Parse JSON metadata if it's a string
                if isinstance(r.get("metadata"), str):
                    import json
                    try:
                        r["metadata"] = json.loads(r["metadata"])
                    except json.JSONDecodeError:
                        r["metadata"] = {}
                reconciliation_responses.append(ReconciliationResponse(**r))
            
            return ReconciliationListResponse(
                reconciliations=reconciliation_responses,
                total=total,
                page=search_request.page,
                size=search_request.size,
                pages=(total + search_request.size - 1) // search_request.size
            )
            
        except Exception as e:
            logger.error("Failed to search reconciliations", error=str(e))
            raise
    
    async def get_reconciliation_stats(self) -> ReconciliationStatsResponse:
        """Get reconciliation statistics."""
        try:
            stats = self.db.get_reconciliation_stats()
            return ReconciliationStatsResponse(**stats)
            
        except Exception as e:
            logger.error("Failed to get reconciliation stats", error=str(e))
            raise
    
    async def process_reconciliation(self, reconciliation_id: uuid.UUID) -> None:
        """Process a reconciliation (background task)."""
        try:
            logger.info("Starting reconciliation processing", reconciliation_id=str(reconciliation_id))
            
            # Get reconciliation
            reconciliation = self.db.get_reconciliation_by_id(str(reconciliation_id))
            
            if not reconciliation:
                logger.error("Reconciliation not found", reconciliation_id=str(reconciliation_id))
                return
            
            # Update status to processing
            reconciliation["status"] = "processing"
            reconciliation["started_at"] = datetime.utcnow()
            
            # Simulate processing time
            import time
            time.sleep(2)  # Simulate processing
            
            # Update reconciliation with mock results
            reconciliation["status"] = "completed"
            reconciliation["completed_at"] = datetime.utcnow()
            reconciliation["is_successful"] = True
            reconciliation["total_transactions"] = 100
            reconciliation["matched_transactions"] = 95
            reconciliation["unmatched_transactions"] = 5
            reconciliation["total_amount"] = Decimal("10000.00")
            reconciliation["matched_amount"] = Decimal("9500.00")
            reconciliation["unmatched_amount"] = Decimal("500.00")
            reconciliation["processing_time_seconds"] = 2
            
            logger.info(
                "Reconciliation completed",
                reconciliation_id=str(reconciliation_id),
                total_transactions=100,
                matched_transactions=95,
                processing_time=2
            )
            
        except Exception as e:
            logger.error("Reconciliation processing failed", reconciliation_id=str(reconciliation_id), error=str(e))
            
            # Update reconciliation with error
            try:
                reconciliation["status"] = "failed"
                reconciliation["is_successful"] = False
                reconciliation["error_message"] = str(e)
            except Exception as commit_error:
                logger.error("Failed to update reconciliation with error", error=str(commit_error))