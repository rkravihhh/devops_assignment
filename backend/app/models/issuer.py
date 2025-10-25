"""
Issuer model for Tier 1 card issuers.
Note: This file is not used with mock database implementation.
"""

# from sqlalchemy import Column, String, DateTime, Boolean, Text
# from sqlalchemy.dialects.postgresql import UUID
# from sqlalchemy.orm import relationship
# from datetime import datetime
# import uuid

# from app.core.database import Base


# class Issuer(Base):
#     """Issuer entity for Tier 1 card issuers."""
#     
#     __tablename__ = "issuers"
#     
#     # Primary key
#     id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
#     
#     # Issuer identifiers
#     issuer_id = Column(String(50), unique=True, nullable=False, index=True)
#     issuer_name = Column(String(200), nullable=False)
#     issuer_code = Column(String(10), nullable=False, unique=True)
#     
#     # Contact information
#     contact_email = Column(String(200), nullable=True)
#     contact_phone = Column(String(20), nullable=True)
#     
#     # API configuration
#     api_endpoint = Column(String(500), nullable=True)
#     api_key = Column(String(200), nullable=True)
#     api_secret = Column(String(200), nullable=True)
#     
#     # Processing configuration
#     reconciliation_frequency = Column(String(20), nullable=False, default="daily")  # daily, weekly, monthly
#     timezone = Column(String(50), nullable=False, default="UTC")
#     
#     # Status flags
#     is_active = Column(Boolean, default=True, nullable=False)
#     is_pci_compliant = Column(Boolean, default=False, nullable=False)
#     
#     # Timestamps
#     created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
#     updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
#     last_reconciliation = Column(DateTime, nullable=True)
#     
#     # Additional configuration
#     configuration = Column(Text, nullable=True)  # JSON string for issuer-specific config
#     notes = Column(Text, nullable=True)
#     
#     # Relationships
#     transactions = relationship("Transaction", back_populates="issuer")
#     reconciliations = relationship("Reconciliation", back_populates="issuer")
#     
#     def __repr__(self):
#         return f"<Issuer(id={self.id}, issuer_name={self.issuer_name}, issuer_code={self.issuer_code})>"