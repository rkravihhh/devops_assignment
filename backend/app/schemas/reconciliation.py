"""
Pydantic schemas for reconciliation-related API requests and responses.
"""

from typing import Optional, Dict, Any
from datetime import datetime
from decimal import Decimal
from pydantic import BaseModel, Field, field_validator
from uuid import UUID


class ReconciliationBase(BaseModel):
    """Base reconciliation schema."""
    reconciliation_id: str = Field(..., description="Unique reconciliation identifier")
    batch_id: Optional[str] = Field(None, description="Batch identifier")
    issuer_id: str = Field(..., description="Issuer identifier")
    reconciliation_type: str = Field(..., description="Type of reconciliation")
    start_date: datetime = Field(..., description="Reconciliation start date")
    end_date: datetime = Field(..., description="Reconciliation end date")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Additional reconciliation metadata")
    notes: Optional[str] = Field(None, description="Reconciliation notes")


class ReconciliationCreate(ReconciliationBase):
    """Schema for creating a new reconciliation."""
    pass


class ReconciliationUpdate(BaseModel):
    """Schema for updating a reconciliation."""
    status: Optional[str] = Field(None, description="Updated reconciliation status")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Updated metadata")
    notes: Optional[str] = Field(None, description="Updated notes")


class ReconciliationResponse(ReconciliationBase):
    """Schema for reconciliation response."""
    id: UUID = Field(..., description="Internal reconciliation ID")
    status: str = Field(..., description="Reconciliation status")
    total_transactions: int = Field(..., description="Total number of transactions")
    matched_transactions: int = Field(..., description="Number of matched transactions")
    unmatched_transactions: int = Field(..., description="Number of unmatched transactions")
    total_amount: Decimal = Field(..., description="Total transaction amount")
    matched_amount: Decimal = Field(..., description="Matched transaction amount")
    unmatched_amount: Decimal = Field(..., description="Unmatched transaction amount")
    started_at: Optional[datetime] = Field(None, description="Processing start time")
    completed_at: Optional[datetime] = Field(None, description="Processing completion time")
    processing_time_seconds: Optional[int] = Field(None, description="Processing time in seconds")
    is_successful: bool = Field(..., description="Whether reconciliation was successful")
    error_message: Optional[str] = Field(None, description="Error message if failed")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")
    
    class Config:
        from_attributes = True


class ReconciliationListResponse(BaseModel):
    """Schema for paginated reconciliation list response."""
    reconciliations: list[ReconciliationResponse] = Field(..., description="List of reconciliations")
    total: int = Field(..., description="Total number of reconciliations")
    page: int = Field(..., description="Current page number")
    size: int = Field(..., description="Page size")
    pages: int = Field(..., description="Total number of pages")


class ReconciliationSearchRequest(BaseModel):
    """Schema for reconciliation search request."""
    issuer_id: Optional[str] = Field(None, description="Filter by issuer ID")
    status: Optional[str] = Field(None, description="Filter by reconciliation status")
    reconciliation_type: Optional[str] = Field(None, description="Filter by reconciliation type")
    start_date: Optional[datetime] = Field(None, description="Filter by start date")
    end_date: Optional[datetime] = Field(None, description="Filter by end date")
    is_successful: Optional[bool] = Field(None, description="Filter by success status")
    page: int = Field(1, ge=1, description="Page number")
    size: int = Field(20, ge=1, le=100, description="Page size")
    sort_by: str = Field("created_at", description="Sort field")
    sort_order: str = Field("desc", description="Sort order (asc/desc)")
    
    @field_validator("sort_order")
    @classmethod
    def validate_sort_order(cls, v):
        if v not in ["asc", "desc"]:
            raise ValueError("sort_order must be 'asc' or 'desc'")
        return v


class ReconciliationStatsResponse(BaseModel):
    """Schema for reconciliation statistics response."""
    total_reconciliations: int = Field(..., description="Total number of reconciliations")
    successful_reconciliations: int = Field(..., description="Number of successful reconciliations")
    failed_reconciliations: int = Field(..., description="Number of failed reconciliations")
    pending_reconciliations: int = Field(..., description="Number of pending reconciliations")
    total_transactions_processed: int = Field(..., description="Total transactions processed")
    total_amount_processed: Decimal = Field(..., description="Total amount processed")
    average_processing_time: Optional[float] = Field(None, description="Average processing time in seconds")
    last_reconciliation: Optional[datetime] = Field(None, description="Last reconciliation timestamp")
