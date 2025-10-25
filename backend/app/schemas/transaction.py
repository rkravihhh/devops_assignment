"""
Pydantic schemas for transaction-related API requests and responses.
Enhanced for PCI DSS Level 1 compliance.
"""

from typing import Optional, Dict, Any, List
from datetime import datetime
from decimal import Decimal
from pydantic import BaseModel, Field, field_validator, validator
from uuid import UUID
import re


class TransactionBase(BaseModel):
    """Base transaction schema with PCI DSS Level 1 compliance."""
    transaction_id: str = Field(..., description="Unique transaction identifier", min_length=1, max_length=50)
    external_id: Optional[str] = Field(None, description="External system transaction ID", max_length=100)
    issuer_transaction_id: Optional[str] = Field(None, description="Issuer's transaction ID", max_length=100)
    issuer_id: str = Field(..., description="Issuer identifier", min_length=1, max_length=50)
    card_number: str = Field(..., description="Card number (will be masked in response)", min_length=13, max_length=19)
    amount: Decimal = Field(..., gt=0, description="Transaction amount", max_digits=15, decimal_places=2)
    currency: str = Field("USD", description="Transaction currency", min_length=3, max_length=3)
    transaction_type: str = Field(..., description="Type of transaction", max_length=20)
    transaction_status: str = Field(..., description="Transaction status", max_length=20)
    merchant_name: Optional[str] = Field(None, description="Merchant name", max_length=200)
    merchant_category: Optional[str] = Field(None, description="Merchant category code", max_length=10)
    merchant_id: Optional[str] = Field(None, description="Merchant identifier", max_length=50)
    merchant_city: Optional[str] = Field(None, description="Merchant city", max_length=100)
    merchant_country: Optional[str] = Field(None, description="Merchant country code", min_length=2, max_length=3)
    transaction_date: datetime = Field(..., description="Transaction date and time")
    settlement_date: Optional[datetime] = Field(None, description="Settlement date")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Additional transaction metadata")
    processing_notes: Optional[str] = Field(None, description="Processing notes", max_length=1000)
    
    @validator('card_number')
    def validate_card_number(cls, v: str) -> str:
        """Validate card number format for PCI compliance."""
        # Remove spaces and dashes
        cleaned = re.sub(r'[\s-]', '', v)
        
        # Check if it's numeric
        if not cleaned.isdigit():
            raise ValueError('Card number must contain only digits')
        
        # Check length
        if len(cleaned) < 13 or len(cleaned) > 19:
            raise ValueError('Card number must be between 13 and 19 digits')
        
        # Luhn algorithm validation
        if not cls._luhn_check(cleaned):
            raise ValueError('Invalid card number')
        
        return cleaned
    
    @validator('currency')
    def validate_currency(cls, v: str) -> str:
        """Validate currency code."""
        if not v.isalpha() or len(v) != 3:
            raise ValueError('Currency must be a 3-letter code')
        return v.upper()
    
    @validator('transaction_type')
    def validate_transaction_type(cls, v: str) -> str:
        """Validate transaction type."""
        allowed_types = ['purchase', 'refund', 'chargeback', 'dispute', 'void']
        if v.lower() not in allowed_types:
            raise ValueError(f'Transaction type must be one of: {", ".join(allowed_types)}')
        return v.lower()
    
    @validator('transaction_status')
    def validate_transaction_status(cls, v: str) -> str:
        """Validate transaction status."""
        allowed_statuses = ['pending', 'completed', 'failed', 'disputed', 'cancelled']
        if v.lower() not in allowed_statuses:
            raise ValueError(f'Transaction status must be one of: {", ".join(allowed_statuses)}')
        return v.lower()
    
    @validator('merchant_country')
    def validate_merchant_country(cls, v: str) -> str:
        """Validate merchant country code."""
        if v and (len(v) < 2 or len(v) > 3):
            raise ValueError('Merchant country must be 2 or 3 character code')
        return v.upper() if v else v
    
    @staticmethod
    def _luhn_check(card_number: str) -> bool:
        """Luhn algorithm for card number validation."""
        def digits_of(n: str) -> List[int]:
            return [int(d) for d in str(n)]
        
        digits = digits_of(card_number)
        odd_digits = digits[-1::-2]
        even_digits = digits[-2::-2]
        checksum = sum(odd_digits)
        for d in even_digits:
            checksum += sum(digits_of(d * 2))
        return checksum % 10 == 0


class TransactionCreate(TransactionBase):
    """Schema for creating a new transaction."""
    pass


class TransactionUpdate(BaseModel):
    """Schema for updating a transaction."""
    transaction_status: Optional[str] = Field(None, description="Updated transaction status")
    settlement_date: Optional[datetime] = Field(None, description="Updated settlement date")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Updated metadata")
    processing_notes: Optional[str] = Field(None, description="Updated processing notes")


class TransactionResponse(TransactionBase):
    """Schema for transaction response."""
    id: UUID = Field(..., description="Internal transaction ID")
    card_number_masked: str = Field(..., description="Masked card number")
    is_reconciled: bool = Field(..., description="Whether transaction is reconciled")
    reconciliation_id: Optional[UUID] = Field(None, description="Associated reconciliation ID")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")
    
    class Config:
        from_attributes = True


class TransactionListResponse(BaseModel):
    """Schema for paginated transaction list response."""
    transactions: list[TransactionResponse] = Field(..., description="List of transactions")
    total: int = Field(..., description="Total number of transactions")
    page: int = Field(..., description="Current page number")
    size: int = Field(..., description="Page size")
    pages: int = Field(..., description="Total number of pages")


class TransactionSearchRequest(BaseModel):
    """Schema for transaction search request."""
    issuer_id: Optional[str] = Field(None, description="Filter by issuer ID")
    transaction_status: Optional[str] = Field(None, description="Filter by transaction status")
    transaction_type: Optional[str] = Field(None, description="Filter by transaction type")
    start_date: Optional[datetime] = Field(None, description="Filter by start date")
    end_date: Optional[datetime] = Field(None, description="Filter by end date")
    min_amount: Optional[Decimal] = Field(None, description="Minimum transaction amount")
    max_amount: Optional[Decimal] = Field(None, description="Maximum transaction amount")
    is_reconciled: Optional[bool] = Field(None, description="Filter by reconciliation status")
    page: int = Field(1, ge=1, description="Page number")
    size: int = Field(20, ge=1, le=100, description="Page size")
    sort_by: str = Field("transaction_date", description="Sort field")
    sort_order: str = Field("desc", description="Sort order (asc/desc)")
    
    @field_validator("sort_order")
    @classmethod
    def validate_sort_order(cls, v):
        if v not in ["asc", "desc"]:
            raise ValueError("sort_order must be 'asc' or 'desc'")
        return v
