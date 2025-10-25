"""
Transaction model for card transaction data.
Note: This file is not used with mock database implementation.
"""

# from sqlalchemy import Column, String, DateTime, Numeric, Integer, Text, Boolean, ForeignKey
# from sqlalchemy.dialects.postgresql import UUID
# from sqlalchemy.orm import relationship
# from datetime import datetime
# import uuid

# from app.core.database import Base


# class Transaction(Base):
#     """Transaction entity for card transactions."""
#     
#     __tablename__ = "transactions"
#     
#     # Primary key
#     id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
#     
#     # Transaction identifiers
#     transaction_id = Column(String(50), unique=True, nullable=False, index=True)
#     external_id = Column(String(100), nullable=True, index=True)
#     issuer_transaction_id = Column(String(100), nullable=True, index=True)
#     
#     # Issuer information
#     issuer_id = Column(String(50), ForeignKey("issuers.id"), nullable=False, index=True)
#     
#     # Transaction details
#     card_number = Column(String(20), nullable=False, index=True)
#     card_number_masked = Column(String(20), nullable=False)
#     amount = Column(Numeric(15, 2), nullable=False)
#     currency = Column(String(3), nullable=False, default="USD")
#     
#     # Transaction metadata
#     transaction_type = Column(String(20), nullable=False)  # purchase, refund, chargeback
#     transaction_status = Column(String(20), nullable=False)  # pending, completed, failed, disputed
#     merchant_name = Column(String(200), nullable=True)
#     merchant_category = Column(String(10), nullable=True)
#     merchant_id = Column(String(50), nullable=True)
#     
#     # Location data
#     merchant_city = Column(String(100), nullable=True)
#     merchant_country = Column(String(3), nullable=True)
#     
#     # Timestamps
#     transaction_date = Column(DateTime, nullable=False, index=True)
#     settlement_date = Column(DateTime, nullable=True)
#     created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
#     updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
#     
#     # Processing flags
#     is_reconciled = Column(Boolean, default=False, nullable=False)
#     reconciliation_id = Column(UUID(as_uuid=True), ForeignKey("reconciliations.id"), nullable=True)
#     
#     # Additional data
#     metadata = Column(Text, nullable=True)  # JSON string for additional data
#     processing_notes = Column(Text, nullable=True)
#     
#     # Relationships
#     issuer = relationship("Issuer", back_populates="transactions")
#     reconciliation = relationship("Reconciliation", back_populates="transactions")
#     
#     def __repr__(self):
#         return f"<Transaction(id={self.id}, transaction_id={self.transaction_id}, amount={self.amount})>"
