"""
Pydantic schemas for issuer-related API requests and responses.
"""

from typing import Optional, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field, field_validator
from uuid import UUID


class IssuerBase(BaseModel):
    """Base issuer schema."""
    issuer_id: str = Field(..., description="Unique issuer identifier")
    issuer_name: str = Field(..., description="Issuer name")
    issuer_code: str = Field(..., description="Issuer code")
    contact_email: Optional[str] = Field(None, description="Contact email")
    contact_phone: Optional[str] = Field(None, description="Contact phone")
    api_endpoint: Optional[str] = Field(None, description="API endpoint URL")
    reconciliation_frequency: str = Field("daily", description="Reconciliation frequency")
    timezone: str = Field("UTC", description="Issuer timezone")
    is_active: bool = Field(True, description="Whether issuer is active")
    is_pci_compliant: bool = Field(False, description="PCI compliance status")
    configuration: Optional[Dict[str, Any]] = Field(None, description="Issuer-specific configuration")
    notes: Optional[str] = Field(None, description="Additional notes")


class IssuerCreate(IssuerBase):
    """Schema for creating a new issuer."""
    pass


class IssuerUpdate(BaseModel):
    """Schema for updating an issuer."""
    issuer_name: Optional[str] = Field(None, description="Updated issuer name")
    contact_email: Optional[str] = Field(None, description="Updated contact email")
    contact_phone: Optional[str] = Field(None, description="Updated contact phone")
    api_endpoint: Optional[str] = Field(None, description="Updated API endpoint")
    reconciliation_frequency: Optional[str] = Field(None, description="Updated reconciliation frequency")
    timezone: Optional[str] = Field(None, description="Updated timezone")
    is_active: Optional[bool] = Field(None, description="Updated active status")
    is_pci_compliant: Optional[bool] = Field(None, description="Updated PCI compliance status")
    configuration: Optional[Dict[str, Any]] = Field(None, description="Updated configuration")
    notes: Optional[str] = Field(None, description="Updated notes")


class IssuerResponse(IssuerBase):
    """Schema for issuer response."""
    id: UUID = Field(..., description="Internal issuer ID")
    last_reconciliation: Optional[datetime] = Field(None, description="Last reconciliation timestamp")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")
    
    class Config:
        from_attributes = True


class IssuerListResponse(BaseModel):
    """Schema for paginated issuer list response."""
    issuers: list[IssuerResponse] = Field(..., description="List of issuers")
    total: int = Field(..., description="Total number of issuers")
    page: int = Field(..., description="Current page number")
    size: int = Field(..., description="Page size")
    pages: int = Field(..., description="Total number of pages")


class IssuerSearchRequest(BaseModel):
    """Schema for issuer search request."""
    issuer_name: Optional[str] = Field(None, description="Filter by issuer name")
    issuer_code: Optional[str] = Field(None, description="Filter by issuer code")
    is_active: Optional[bool] = Field(None, description="Filter by active status")
    is_pci_compliant: Optional[bool] = Field(None, description="Filter by PCI compliance")
    page: int = Field(1, ge=1, description="Page number")
    size: int = Field(20, ge=1, le=100, description="Page size")
    sort_by: str = Field("issuer_name", description="Sort field")
    sort_order: str = Field("asc", description="Sort order (asc/desc)")
    
    @field_validator("sort_order")
    @classmethod
    def validate_sort_order(cls, v):
        if v not in ["asc", "desc"]:
            raise ValueError("sort_order must be 'asc' or 'desc'")
        return v
