"""
Reconciliation endpoints.
"""

from fastapi import APIRouter, Depends, HTTPException, Query, BackgroundTasks

from app.core.database import get_db
from app.schemas.reconciliation import (
    ReconciliationCreate, 
    ReconciliationUpdate, 
    ReconciliationResponse, 
    ReconciliationListResponse,
    ReconciliationSearchRequest,
    ReconciliationStatsResponse
)
from app.services.reconciliation_service import ReconciliationService

router = APIRouter()


@router.post("/", response_model=ReconciliationResponse, status_code=201)
async def create_reconciliation(
    reconciliation: ReconciliationCreate,
    background_tasks: BackgroundTasks,
    db = Depends(get_db)
):
    """Create a new reconciliation."""
    service = ReconciliationService(db)
    result = await service.create_reconciliation(reconciliation)
    
    # Start reconciliation process in background
    background_tasks.add_task(service.process_reconciliation, result.id)
    
    return result


@router.get("/{reconciliation_id}", response_model=ReconciliationResponse)
async def get_reconciliation(
    reconciliation_id: str,
    db = Depends(get_db)
):
    """Get a reconciliation by ID."""
    service = ReconciliationService(db)
    reconciliation = await service.get_reconciliation_by_id(reconciliation_id)
    if not reconciliation:
        raise HTTPException(status_code=404, detail="Reconciliation not found")
    return reconciliation


@router.put("/{reconciliation_id}", response_model=ReconciliationResponse)
async def update_reconciliation(
    reconciliation_id: str,
    reconciliation_update: ReconciliationUpdate,
    db = Depends(get_db)
):
    """Update a reconciliation."""
    service = ReconciliationService(db)
    reconciliation = await service.update_reconciliation(reconciliation_id, reconciliation_update)
    if not reconciliation:
        raise HTTPException(status_code=404, detail="Reconciliation not found")
    return reconciliation


@router.delete("/{reconciliation_id}", status_code=204)
async def delete_reconciliation(
    reconciliation_id: str,
    db = Depends(get_db)
):
    """Delete a reconciliation."""
    service = ReconciliationService(db)
    success = await service.delete_reconciliation(reconciliation_id)
    if not success:
        raise HTTPException(status_code=404, detail="Reconciliation not found")


@router.get("/", response_model=ReconciliationListResponse)
async def search_reconciliations(
    issuer_id: str = Query(None, description="Filter by issuer ID"),
    status: str = Query(None, description="Filter by reconciliation status"),
    reconciliation_type: str = Query(None, description="Filter by reconciliation type"),
    start_date: str = Query(None, description="Filter by start date (ISO format)"),
    end_date: str = Query(None, description="Filter by end date (ISO format)"),
    is_successful: bool = Query(None, description="Filter by success status"),
    page: int = Query(1, ge=1, description="Page number"),
    size: int = Query(20, ge=1, le=100, description="Page size"),
    sort_by: str = Query("created_at", description="Sort field"),
    sort_order: str = Query("desc", description="Sort order"),
    db = Depends(get_db)
):
    """Search reconciliations with filters."""
    service = ReconciliationService(db)
    search_request = ReconciliationSearchRequest(
        issuer_id=issuer_id,
        status=status,
        reconciliation_type=reconciliation_type,
        start_date=start_date,
        end_date=end_date,
        is_successful=is_successful,
        page=page,
        size=size,
        sort_by=sort_by,
        sort_order=sort_order
    )
    return await service.search_reconciliations(search_request)


@router.get("/stats/overview", response_model=ReconciliationStatsResponse)
async def get_reconciliation_stats(
    db = Depends(get_db)
):
    """Get reconciliation statistics overview."""
    service = ReconciliationService(db)
    return await service.get_reconciliation_stats()


@router.post("/{reconciliation_id}/process", response_model=ReconciliationResponse)
async def process_reconciliation(
    reconciliation_id: str,
    background_tasks: BackgroundTasks,
    db = Depends(get_db)
):
    """Manually trigger reconciliation processing."""
    service = ReconciliationService(db)
    reconciliation = await service.get_reconciliation_by_id(reconciliation_id)
    if not reconciliation:
        raise HTTPException(status_code=404, detail="Reconciliation not found")
    
    # Start processing in background
    background_tasks.add_task(service.process_reconciliation, reconciliation.id)
    
    return reconciliation
