"""
Transaction service for business logic.
"""

from typing import Optional, List
from typing import Dict, Any
from datetime import datetime
import structlog

from app.schemas.transaction import (
    TransactionCreate, 
    TransactionUpdate, 
    TransactionResponse, 
    TransactionListResponse,
    TransactionSearchRequest
)
from app.core.exceptions import TransactionNotFoundError

logger = structlog.get_logger()


class TransactionService:
    """Service for transaction operations."""
    
    def __init__(self, db) -> None:
        self.db = db
    
    async def create_transaction(self, transaction_data: TransactionCreate) -> TransactionResponse:
        """Create a new transaction."""
        try:
            # Convert Pydantic model to dict
            transaction_dict = transaction_data.model_dump()
            
            # Create transaction using mock database
            transaction = self.db.create_transaction(transaction_dict)

            # Parse JSON metadata if it's a string
            if isinstance(transaction.get("metadata"), str):
                import json
                try:
                    transaction["metadata"] = json.loads(transaction["metadata"])
                except json.JSONDecodeError:
                    transaction["metadata"] = {}

            logger.info("Transaction created", transaction_id=transaction["transaction_id"])
            return TransactionResponse(**transaction)
            
        except Exception as e:
            logger.error("Failed to create transaction", error=str(e))
            raise
    
    async def get_transaction_by_id(self, transaction_id: str) -> Optional[TransactionResponse]:
        """Get a transaction by ID."""
        try:
            transaction = self.db.get_transaction_by_id(transaction_id)
            
            if not transaction:
                return None
            
            # Parse JSON metadata if it's a string
            if isinstance(transaction.get("metadata"), str):
                import json
                try:
                    transaction["metadata"] = json.loads(transaction["metadata"])
                except json.JSONDecodeError:
                    transaction["metadata"] = {}
                
            return TransactionResponse(**transaction)
            
        except Exception as e:
            logger.error("Failed to get transaction", transaction_id=transaction_id, error=str(e))
            raise
    
    async def update_transaction(self, transaction_id: str, update_data: TransactionUpdate) -> Optional[TransactionResponse]:
        """Update a transaction."""
        try:
            # Convert Pydantic model to dict, excluding None values
            update_dict = {k: v for k, v in update_data.model_dump().items() if v is not None}
            
            transaction = self.db.update_transaction(transaction_id, update_dict)
            
            if not transaction:
                return None
            
            logger.info("Transaction updated", transaction_id=transaction_id)
            return TransactionResponse(**transaction)
            
        except Exception as e:
            logger.error("Failed to update transaction", transaction_id=transaction_id, error=str(e))
            raise
    
    async def delete_transaction(self, transaction_id: str) -> bool:
        """Delete a transaction."""
        try:
            success = self.db.delete_transaction(transaction_id)
            
            if success:
                logger.info("Transaction deleted", transaction_id=transaction_id)
            else:
                logger.warning("Transaction not found for deletion", transaction_id=transaction_id)
            
            return success
            
        except Exception as e:
            logger.error("Failed to delete transaction", transaction_id=transaction_id, error=str(e))
            raise
    
    async def search_transactions(self, search_request: TransactionSearchRequest) -> TransactionListResponse:
        """Search transactions with filters."""
        try:
            # Convert search request to filters dict
            filters = {
                "issuer_id": search_request.issuer_id,
                "transaction_status": search_request.transaction_status,
                "transaction_type": search_request.transaction_type,
                "is_reconciled": search_request.is_reconciled
            }
            
            # Get filtered results
            transactions = self.db.search_transactions(filters)
            
            # Apply pagination
            total = len(transactions)
            start_idx = (search_request.page - 1) * search_request.size
            end_idx = start_idx + search_request.size
            paginated_transactions = transactions[start_idx:end_idx]
            
            # Convert to response objects, parsing JSON metadata
            transaction_responses = []
            for t in paginated_transactions:
                # Parse JSON metadata if it's a string
                if isinstance(t.get("metadata"), str):
                    import json
                    try:
                        t["metadata"] = json.loads(t["metadata"])
                    except json.JSONDecodeError:
                        t["metadata"] = {}
                transaction_responses.append(TransactionResponse(**t))
            
            return TransactionListResponse(
                transactions=transaction_responses,
                total=total,
                page=search_request.page,
                size=search_request.size,
                pages=(total + search_request.size - 1) // search_request.size
            )
            
        except Exception as e:
            logger.error("Failed to search transactions", error=str(e))
            raise
    
    async def get_transactions_by_issuer(self, issuer_id: str, page: int, size: int) -> TransactionListResponse:
        """Get all transactions for a specific issuer."""
        search_request = TransactionSearchRequest(
            issuer_id=issuer_id,
            page=page,
            size=size
        )
        return await self.search_transactions(search_request)
