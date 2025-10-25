"""
Issuer service for business logic.
"""

from typing import Optional
from datetime import datetime
import structlog

from app.schemas.issuer import (
    IssuerCreate, 
    IssuerUpdate, 
    IssuerResponse, 
    IssuerListResponse,
    IssuerSearchRequest
)
from app.core.exceptions import IssuerNotFoundError

logger = structlog.get_logger()


class IssuerService:
    """Service for issuer operations."""
    
    def __init__(self, db) -> None:
        self.db = db
    
    async def create_issuer(self, issuer_data: IssuerCreate) -> IssuerResponse:
        """Create a new issuer."""
        try:
            # Convert Pydantic model to dict
            issuer_dict = issuer_data.model_dump()
            
            # Create issuer using mock database
            issuer = self.db.create_issuer(issuer_dict)
            
            # Parse JSON configuration if it's a string
            if isinstance(issuer.get("configuration"), str):
                import json
                try:
                    issuer["configuration"] = json.loads(issuer["configuration"])
                except json.JSONDecodeError:
                    issuer["configuration"] = {}

            logger.info("Issuer created", issuer_id=issuer["issuer_id"])
            return IssuerResponse(**issuer)
            
        except Exception as e:
            logger.error("Failed to create issuer", error=str(e))
            raise
    
    async def get_issuer_by_id(self, issuer_id: str) -> Optional[IssuerResponse]:
        """Get an issuer by ID."""
        try:
            issuer = self.db.get_issuer_by_id(issuer_id)
            
            if not issuer:
                return None
            
            # Parse JSON configuration if it's a string
            if isinstance(issuer.get("configuration"), str):
                import json
                try:
                    issuer["configuration"] = json.loads(issuer["configuration"])
                except json.JSONDecodeError:
                    issuer["configuration"] = {}
                
            return IssuerResponse(**issuer)
            
        except Exception as e:
            logger.error("Failed to get issuer", issuer_id=issuer_id, error=str(e))
            raise
    
    async def update_issuer(self, issuer_id: str, update_data: IssuerUpdate) -> Optional[IssuerResponse]:
        """Update an issuer."""
        try:
            # Convert Pydantic model to dict, excluding None values
            update_dict = {k: v for k, v in update_data.model_dump().items() if v is not None}
            
            issuer = self.db.update_issuer(issuer_id, update_dict)
            
            if not issuer:
                return None
            
            logger.info("Issuer updated", issuer_id=issuer_id)
            return IssuerResponse(**issuer)
            
        except Exception as e:
            logger.error("Failed to update issuer", issuer_id=issuer_id, error=str(e))
            raise
    
    async def delete_issuer(self, issuer_id: str) -> bool:
        """Delete an issuer."""
        try:
            success: bool = self.db.delete_issuer(issuer_id)
            
            if success:
                logger.info("Issuer deleted", issuer_id=issuer_id)
            else:
                logger.warning("Issuer not found for deletion", issuer_id=issuer_id)
            
            return success
            
        except Exception as e:
            logger.error("Failed to delete issuer", issuer_id=issuer_id, error=str(e))
            raise
    
    async def search_issuers(self, search_request: IssuerSearchRequest) -> IssuerListResponse:
        """Search issuers with filters."""
        try:
            # Convert search request to filters dict
            filters = {
                "issuer_name": search_request.issuer_name,
                "issuer_code": search_request.issuer_code,
                "is_active": search_request.is_active,
                "is_pci_compliant": search_request.is_pci_compliant
            }
            
            # Get filtered results
            issuers = self.db.search_issuers(filters)
            
            # Apply pagination
            total = len(issuers)
            start_idx = (search_request.page - 1) * search_request.size
            end_idx = start_idx + search_request.size
            paginated_issuers = issuers[start_idx:end_idx]
            
            # Convert to response objects, parsing JSON configuration
            issuer_responses = []
            for i in paginated_issuers:
                # Parse JSON configuration if it's a string
                if isinstance(i.get("configuration"), str):
                    import json
                    try:
                        i["configuration"] = json.loads(i["configuration"])
                    except json.JSONDecodeError:
                        i["configuration"] = {}
                issuer_responses.append(IssuerResponse(**i))
            
            return IssuerListResponse(
                issuers=issuer_responses,
                total=total,
                page=search_request.page,
                size=search_request.size,
                pages=(total + search_request.size - 1) // search_request.size
            )
            
        except Exception as e:
            logger.error("Failed to search issuers", error=str(e))
            raise