"""
Issuer endpoints.
"""

from fastapi import APIRouter, Depends, HTTPException, Query

from app.core.database import get_db
from app.schemas.issuer import (
    IssuerCreate, 
    IssuerUpdate, 
    IssuerResponse, 
    IssuerListResponse,
    IssuerSearchRequest
)
from app.services.issuer_service import IssuerService

router = APIRouter()


@router.post("/", response_model=IssuerResponse, status_code=201)
async def create_issuer(
    issuer: IssuerCreate,
    db = Depends(get_db)
):
    """Create a new issuer."""
    service = IssuerService(db)
    return await service.create_issuer(issuer)


@router.get("/{issuer_id}", response_model=IssuerResponse)
async def get_issuer(
    issuer_id: str,
    db = Depends(get_db)
):
    """Get an issuer by ID."""
    service = IssuerService(db)
    issuer = await service.get_issuer_by_id(issuer_id)
    if not issuer:
        raise HTTPException(status_code=404, detail="Issuer not found")
    return issuer


@router.put("/{issuer_id}", response_model=IssuerResponse)
async def update_issuer(
    issuer_id: str,
    issuer_update: IssuerUpdate,
    db = Depends(get_db)
):
    """Update an issuer."""
    service = IssuerService(db)
    issuer = await service.update_issuer(issuer_id, issuer_update)
    if not issuer:
        raise HTTPException(status_code=404, detail="Issuer not found")
    return issuer


@router.delete("/{issuer_id}", status_code=204)
async def delete_issuer(
    issuer_id: str,
    db = Depends(get_db)
):
    """Delete an issuer."""
    service = IssuerService(db)
    success = await service.delete_issuer(issuer_id)
    if not success:
        raise HTTPException(status_code=404, detail="Issuer not found")


@router.get("/", response_model=IssuerListResponse)
async def search_issuers(
    issuer_name: str = Query(None, description="Filter by issuer name"),
    issuer_code: str = Query(None, description="Filter by issuer code"),
    is_active: bool = Query(None, description="Filter by active status"),
    is_pci_compliant: bool = Query(None, description="Filter by PCI compliance"),
    page: int = Query(1, ge=1, description="Page number"),
    size: int = Query(20, ge=1, le=100, description="Page size"),
    sort_by: str = Query("issuer_name", description="Sort field"),
    sort_order: str = Query("asc", description="Sort order"),
    db = Depends(get_db)
):
    """Search issuers with filters."""
    service = IssuerService(db)
    search_request = IssuerSearchRequest(
        issuer_name=issuer_name,
        issuer_code=issuer_code,
        is_active=is_active,
        is_pci_compliant=is_pci_compliant,
        page=page,
        size=size,
        sort_by=sort_by,
        sort_order=sort_order
    )
    return await service.search_issuers(search_request)
