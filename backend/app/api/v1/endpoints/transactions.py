"""
Transaction endpoints with PCI DSS Level 1 compliance.
"""

from typing import List
from fastapi import APIRouter, Depends, HTTPException, Query, Request
from uuid import UUID

from app.core.database import get_db
from app.core.auth import (
    get_current_user_api_key, 
    require_permission, 
    require_issuer_access,
    PCIAuditLogger
)
from app.schemas.transaction import (
    TransactionCreate, 
    TransactionUpdate, 
    TransactionResponse, 
    TransactionListResponse,
    TransactionSearchRequest
)
from app.services.transaction_service import TransactionService

router = APIRouter()


@router.post("/", response_model=TransactionResponse, status_code=201)
async def create_transaction(
    transaction: TransactionCreate,
    request: Request,
    current_user = Depends(require_permission("write")),
    db = Depends(get_db)
):
    """Create a new transaction with PCI DSS compliance."""
    # Log transaction creation for PCI audit
    PCIAuditLogger.log_transaction_access(
        user_id=current_user.get("issuer_id"),
        action="create_transaction",
        success=True
    )
    
    service = TransactionService(db)
    result = await service.create_transaction(transaction)
    
    # Log successful creation
    PCIAuditLogger.log_transaction_access(
        user_id=current_user.get("issuer_id"),
        action="transaction_created",
        transaction_id=result.transaction_id,
        issuer_id=result.issuer_id,
        success=True
    )
    
    return result


@router.get("/{transaction_id}", response_model=TransactionResponse)
async def get_transaction(
    transaction_id: str,
    current_user = Depends(require_issuer_access()),
    db = Depends(get_db)
):
    """Get a transaction by ID with PCI DSS compliance."""
    service = TransactionService(db)
    transaction = await service.get_transaction_by_id(transaction_id)
    if not transaction:
        PCIAuditLogger.log_transaction_access(
            user_id=current_user.get("issuer_id"),
            action="get_transaction",
            transaction_id=transaction_id,
            success=False
        )
        raise HTTPException(status_code=404, detail="Transaction not found")
    
    # Log successful access
    PCIAuditLogger.log_transaction_access(
        user_id=current_user.get("issuer_id"),
        action="get_transaction",
        transaction_id=transaction_id,
        issuer_id=transaction.issuer_id,
        success=True
    )
    
    return transaction


@router.put("/{transaction_id}", response_model=TransactionResponse)
async def update_transaction(
    transaction_id: str,
    transaction_update: TransactionUpdate,
    current_user = Depends(require_permission("write")),
    db = Depends(get_db)
):
    """Update a transaction with PCI DSS compliance."""
    service = TransactionService(db)
    transaction = await service.update_transaction(transaction_id, transaction_update)
    if not transaction:
        PCIAuditLogger.log_transaction_access(
            user_id=current_user.get("issuer_id"),
            action="update_transaction",
            transaction_id=transaction_id,
            success=False
        )
        raise HTTPException(status_code=404, detail="Transaction not found")
    
    # Log successful update
    PCIAuditLogger.log_transaction_access(
        user_id=current_user.get("issuer_id"),
        action="update_transaction",
        transaction_id=transaction_id,
        issuer_id=transaction.issuer_id,
        success=True
    )
    
    return transaction


@router.delete("/{transaction_id}", status_code=204)
async def delete_transaction(
    transaction_id: str,
    current_user = Depends(require_permission("write")),
    db = Depends(get_db)
):
    """Delete a transaction with PCI DSS compliance."""
    service = TransactionService(db)
    success = await service.delete_transaction(transaction_id)
    if not success:
        PCIAuditLogger.log_transaction_access(
            user_id=current_user.get("issuer_id"),
            action="delete_transaction",
            transaction_id=transaction_id,
            success=False
        )
        raise HTTPException(status_code=404, detail="Transaction not found")
    
    # Log successful deletion
    PCIAuditLogger.log_transaction_access(
        user_id=current_user.get("issuer_id"),
        action="delete_transaction",
        transaction_id=transaction_id,
        success=True
    )


@router.get("/", response_model=TransactionListResponse)
async def search_transactions(
    issuer_id: str = Query(None, description="Filter by issuer ID"),
    transaction_status: str = Query(None, description="Filter by transaction status"),
    transaction_type: str = Query(None, description="Filter by transaction type"),
    start_date: str = Query(None, description="Filter by start date (ISO format)"),
    end_date: str = Query(None, description="Filter by end date (ISO format)"),
    is_reconciled: bool = Query(None, description="Filter by reconciliation status"),
    page: int = Query(1, ge=1, description="Page number"),
    size: int = Query(20, ge=1, le=100, description="Page size"),
    sort_by: str = Query("transaction_date", description="Sort field"),
    sort_order: str = Query("desc", description="Sort order"),
    current_user = Depends(require_issuer_access()),
    db = Depends(get_db)
):
    """Search transactions with filters and PCI DSS compliance."""
    # Log search access
    PCIAuditLogger.log_transaction_access(
        user_id=current_user.get("issuer_id"),
        action="search_transactions",
        success=True,
        details={
            "issuer_id": issuer_id,
            "transaction_status": transaction_status,
            "transaction_type": transaction_type,
            "page": page,
            "size": size
        }
    )
    
    service = TransactionService(db)
    search_request = TransactionSearchRequest(
        issuer_id=issuer_id,
        transaction_status=transaction_status,
        transaction_type=transaction_type,
        start_date=start_date,
        end_date=end_date,
        is_reconciled=is_reconciled,
        page=page,
        size=size,
        sort_by=sort_by,
        sort_order=sort_order
    )
    return await service.search_transactions(search_request)


@router.get("/issuer/{issuer_id}", response_model=TransactionListResponse)
async def get_transactions_by_issuer(
    issuer_id: str,
    page: int = Query(1, ge=1, description="Page number"),
    size: int = Query(20, ge=1, le=100, description="Page size"),
    current_user = Depends(require_issuer_access()),
    db = Depends(get_db)
):
    """Get all transactions for a specific issuer with PCI DSS compliance."""
    # Verify issuer access
    if current_user.get("issuer_id") != issuer_id:
        PCIAuditLogger.log_transaction_access(
            user_id=current_user.get("issuer_id"),
            action="get_transactions_by_issuer",
            issuer_id=issuer_id,
            success=False
        )
        raise HTTPException(status_code=403, detail="Access denied to issuer data")
    
    # Log access
    PCIAuditLogger.log_transaction_access(
        user_id=current_user.get("issuer_id"),
        action="get_transactions_by_issuer",
        issuer_id=issuer_id,
        success=True
    )
    
    service = TransactionService(db)
    return await service.get_transactions_by_issuer(issuer_id, page, size)
