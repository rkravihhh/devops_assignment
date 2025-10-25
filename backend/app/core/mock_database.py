"""
Mock database implementation for testing without PostgreSQL.
"""

from typing import Dict, List, Any, Optional
from datetime import datetime
from decimal import Decimal
import uuid
import json

# Mock data storage
mock_data: Dict[str, List[Any]] = {
    "transactions": [],
    "issuers": [],
    "reconciliations": []
}

# Sample data for testing
sample_issuers = [
    {
        "id": str(uuid.uuid4()),
        "issuer_id": "ISSUER-001",
        "issuer_name": "Chase Bank",
        "issuer_code": "CHASE",
        "contact_email": "api@chase.com",
        "contact_phone": "+1-800-935-9935",
        "api_endpoint": "https://api.chase.com/v1",
        "reconciliation_frequency": "daily",
        "timezone": "America/New_York",
        "is_active": True,
        "is_pci_compliant": True,
        "configuration": '{"api_version": "v1", "rate_limit": 1000}',
        "notes": "Primary Chase Bank integration",
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow(),
        "last_reconciliation": None
    },
    {
        "id": str(uuid.uuid4()),
        "issuer_id": "ISSUER-002", 
        "issuer_name": "Bank of America",
        "issuer_code": "BOFA",
        "contact_email": "api@bankofamerica.com",
        "contact_phone": "+1-800-432-1000",
        "api_endpoint": "https://api.bankofamerica.com/v1",
        "reconciliation_frequency": "daily",
        "timezone": "America/New_York",
        "is_active": True,
        "is_pci_compliant": True,
        "configuration": '{"api_version": "v1", "rate_limit": 1500}',
        "notes": "Bank of America integration",
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow(),
        "last_reconciliation": None
    }
]

sample_transactions = [
    {
        "id": str(uuid.uuid4()),
        "transaction_id": "TXN-001",
        "external_id": "EXT-001",
        "issuer_transaction_id": "CHASE-001",
        "issuer_id": "ISSUER-001",
        "card_number": "4111111111111111",
        "card_number_masked": "4111****1111",
        "amount": Decimal("100.50"),
        "currency": "USD",
        "transaction_type": "purchase",
        "transaction_status": "completed",
        "merchant_name": "Amazon.com",
        "merchant_category": "5999",
        "merchant_id": "AMZN-001",
        "merchant_city": "Seattle",
        "merchant_country": "US",
        "transaction_date": datetime(2024, 1, 1, 10, 0, 0),
        "settlement_date": datetime(2024, 1, 2, 0, 0, 0),
        "is_reconciled": False,
        "reconciliation_id": None,
        "metadata": '{"merchant_type": "online", "fraud_score": 0.1}',
        "processing_notes": "Standard processing",
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow()
    },
    {
        "id": str(uuid.uuid4()),
        "transaction_id": "TXN-002",
        "external_id": "EXT-002",
        "issuer_transaction_id": "BOFA-002",
        "issuer_id": "ISSUER-002",
        "card_number": "5555555555554444",
        "card_number_masked": "5555****4444",
        "amount": Decimal("250.00"),
        "currency": "USD",
        "transaction_type": "purchase",
        "transaction_status": "completed",
        "merchant_name": "Starbucks",
        "merchant_category": "5814",
        "merchant_id": "SBUX-001",
        "merchant_city": "New York",
        "merchant_country": "US",
        "transaction_date": datetime(2024, 1, 1, 14, 30, 0),
        "settlement_date": datetime(2024, 1, 2, 0, 0, 0),
        "is_reconciled": True,
        "reconciliation_id": str(uuid.uuid4()),
        "metadata": '{"merchant_type": "retail", "fraud_score": 0.05}',
        "processing_notes": "Reconciled successfully",
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow()
    }
]

sample_reconciliations = [
    {
        "id": str(uuid.uuid4()),
        "reconciliation_id": "REC-001",
        "batch_id": "BATCH-001",
        "issuer_id": "ISSUER-001",
        "reconciliation_type": "daily",
        "status": "completed",
        "start_date": datetime(2024, 1, 1, 0, 0, 0),
        "end_date": datetime(2024, 1, 1, 23, 59, 59),
        "total_transactions": 150,
        "matched_transactions": 148,
        "unmatched_transactions": 2,
        "total_amount": Decimal("15750.00"),
        "matched_amount": Decimal("15600.00"),
        "unmatched_amount": Decimal("150.00"),
        "started_at": datetime(2024, 1, 2, 2, 0, 0),
        "completed_at": datetime(2024, 1, 2, 2, 15, 0),
        "processing_time_seconds": 900,
        "is_successful": True,
        "error_message": None,
        "metadata": '{"processing_mode": "batch", "version": "1.0"}',
        "notes": "Daily reconciliation completed successfully",
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow()
    }
]

# Initialize mock data
mock_data["issuers"] = sample_issuers.copy()
mock_data["transactions"] = sample_transactions.copy()
mock_data["reconciliations"] = sample_reconciliations.copy()


class MockDatabase:
    """Mock database implementation."""
    
    def __init__(self) -> None:
        self.data = mock_data
    
    def get_transaction_by_id(self, transaction_id: str) -> Optional[Dict[str, Any]]:
        """Get transaction by transaction_id."""
        for transaction in self.data["transactions"]:
            if transaction["transaction_id"] == transaction_id:
                return transaction
        return None
    
    def get_issuer_by_id(self, issuer_id: str) -> Optional[Dict[str, Any]]:
        """Get issuer by issuer_id."""
        for issuer in self.data["issuers"]:
            if issuer["issuer_id"] == issuer_id:
                return issuer
        return None
    
    def get_reconciliation_by_id(self, reconciliation_id: str) -> Optional[Dict[str, Any]]:
        """Get reconciliation by reconciliation_id."""
        for reconciliation in self.data["reconciliations"]:
            if reconciliation["reconciliation_id"] == reconciliation_id:
                return reconciliation
        return None
    
    def create_transaction(self, transaction_data: Dict) -> Dict:
        """Create a new transaction."""
        transaction = {
            "id": str(uuid.uuid4()),
            "transaction_id": transaction_data["transaction_id"],
            "external_id": transaction_data.get("external_id"),
            "issuer_transaction_id": transaction_data.get("issuer_transaction_id"),
            "issuer_id": transaction_data["issuer_id"],
            "card_number": transaction_data["card_number"],
            "card_number_masked": self._mask_card_number(transaction_data["card_number"]),
            "amount": Decimal(str(transaction_data["amount"])),
            "currency": transaction_data.get("currency", "USD"),
            "transaction_type": transaction_data["transaction_type"],
            "transaction_status": transaction_data["transaction_status"],
            "merchant_name": transaction_data.get("merchant_name"),
            "merchant_category": transaction_data.get("merchant_category"),
            "merchant_id": transaction_data.get("merchant_id"),
            "merchant_city": transaction_data.get("merchant_city"),
            "merchant_country": transaction_data.get("merchant_country"),
            "transaction_date": transaction_data["transaction_date"],
            "settlement_date": transaction_data.get("settlement_date"),
            "is_reconciled": False,
            "reconciliation_id": None,
            "metadata": json.dumps(transaction_data.get("metadata", {})),
            "processing_notes": transaction_data.get("processing_notes"),
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
        self.data["transactions"].append(transaction)
        return transaction
    
    def create_issuer(self, issuer_data: Dict) -> Dict:
        """Create a new issuer."""
        issuer = {
            "id": str(uuid.uuid4()),
            "issuer_id": issuer_data["issuer_id"],
            "issuer_name": issuer_data["issuer_name"],
            "issuer_code": issuer_data["issuer_code"],
            "contact_email": issuer_data.get("contact_email"),
            "contact_phone": issuer_data.get("contact_phone"),
            "api_endpoint": issuer_data.get("api_endpoint"),
            "reconciliation_frequency": issuer_data.get("reconciliation_frequency", "daily"),
            "timezone": issuer_data.get("timezone", "UTC"),
            "is_active": issuer_data.get("is_active", True),
            "is_pci_compliant": issuer_data.get("is_pci_compliant", False),
            "configuration": json.dumps(issuer_data.get("configuration", {})),
            "notes": issuer_data.get("notes"),
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
            "last_reconciliation": None
        }
        self.data["issuers"].append(issuer)
        return issuer
    
    def create_reconciliation(self, reconciliation_data: Dict) -> Dict:
        """Create a new reconciliation."""
        reconciliation = {
            "id": str(uuid.uuid4()),
            "reconciliation_id": reconciliation_data["reconciliation_id"],
            "batch_id": reconciliation_data.get("batch_id"),
            "issuer_id": reconciliation_data["issuer_id"],
            "reconciliation_type": reconciliation_data["reconciliation_type"],
            "status": "pending",
            "start_date": reconciliation_data["start_date"],
            "end_date": reconciliation_data["end_date"],
            "total_transactions": 0,
            "matched_transactions": 0,
            "unmatched_transactions": 0,
            "total_amount": Decimal("0.00"),
            "matched_amount": Decimal("0.00"),
            "unmatched_amount": Decimal("0.00"),
            "started_at": None,
            "completed_at": None,
            "processing_time_seconds": None,
            "is_successful": False,
            "error_message": None,
            "metadata": json.dumps(reconciliation_data.get("metadata", {})),
            "notes": reconciliation_data.get("notes"),
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
        self.data["reconciliations"].append(reconciliation)
        return reconciliation
    
    def update_transaction(self, transaction_id: str, update_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Update a transaction."""
        for i, transaction in enumerate(self.data["transactions"]):
            if transaction["transaction_id"] == transaction_id:
                for key, value in update_data.items():
                    if value is not None:
                        transaction[key] = value
                transaction["updated_at"] = datetime.utcnow()
                return transaction
        return None
    
    def update_issuer(self, issuer_id: str, update_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Update an issuer."""
        for i, issuer in enumerate(self.data["issuers"]):
            if issuer["issuer_id"] == issuer_id:
                for key, value in update_data.items():
                    if value is not None:
                        issuer[key] = value
                issuer["updated_at"] = datetime.utcnow()
                return issuer
        return None
    
    def update_reconciliation(self, reconciliation_id: str, update_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Update a reconciliation."""
        for i, reconciliation in enumerate(self.data["reconciliations"]):
            if reconciliation["reconciliation_id"] == reconciliation_id:
                for key, value in update_data.items():
                    if value is not None:
                        reconciliation[key] = value
                reconciliation["updated_at"] = datetime.utcnow()
                return reconciliation
        return None
    
    def delete_transaction(self, transaction_id: str) -> bool:
        """Delete a transaction."""
        for i, transaction in enumerate(self.data["transactions"]):
            if transaction["transaction_id"] == transaction_id:
                del self.data["transactions"][i]
                return True
        return False
    
    def delete_issuer(self, issuer_id: str) -> bool:
        """Delete an issuer."""
        for i, issuer in enumerate(self.data["issuers"]):
            if issuer["issuer_id"] == issuer_id:
                del self.data["issuers"][i]
                return True
        return False
    
    def delete_reconciliation(self, reconciliation_id: str) -> bool:
        """Delete a reconciliation."""
        for i, reconciliation in enumerate(self.data["reconciliations"]):
            if reconciliation["reconciliation_id"] == reconciliation_id:
                del self.data["reconciliations"][i]
                return True
        return False
    
    def search_transactions(self, filters: Dict) -> List[Dict]:
        """Search transactions with filters."""
        results = self.data["transactions"].copy()
        
        # Apply filters
        if filters.get("issuer_id"):
            results = [t for t in results if t["issuer_id"] == filters["issuer_id"]]
        if filters.get("transaction_status"):
            results = [t for t in results if t["transaction_status"] == filters["transaction_status"]]
        if filters.get("transaction_type"):
            results = [t for t in results if t["transaction_type"] == filters["transaction_type"]]
        if filters.get("is_reconciled") is not None:
            results = [t for t in results if t["is_reconciled"] == filters["is_reconciled"]]
        
        return results
    
    def search_issuers(self, filters: Dict) -> List[Dict]:
        """Search issuers with filters."""
        results = self.data["issuers"].copy()
        
        # Apply filters
        if filters.get("issuer_name"):
            results = [i for i in results if filters["issuer_name"].lower() in i["issuer_name"].lower()]
        if filters.get("issuer_code"):
            results = [i for i in results if i["issuer_code"] == filters["issuer_code"]]
        if filters.get("is_active") is not None:
            results = [i for i in results if i["is_active"] == filters["is_active"]]
        if filters.get("is_pci_compliant") is not None:
            results = [i for i in results if i["is_pci_compliant"] == filters["is_pci_compliant"]]
        
        return results
    
    def search_reconciliations(self, filters: Dict) -> List[Dict]:
        """Search reconciliations with filters."""
        results = self.data["reconciliations"].copy()
        
        # Apply filters
        if filters.get("issuer_id"):
            results = [r for r in results if r["issuer_id"] == filters["issuer_id"]]
        if filters.get("status"):
            results = [r for r in results if r["status"] == filters["status"]]
        if filters.get("reconciliation_type"):
            results = [r for r in results if r["reconciliation_type"] == filters["reconciliation_type"]]
        if filters.get("is_successful") is not None:
            results = [r for r in results if r["is_successful"] == filters["is_successful"]]
        
        return results
    
    def get_reconciliation_stats(self) -> Dict:
        """Get reconciliation statistics."""
        reconciliations = self.data["reconciliations"]
        
        total_reconciliations = len(reconciliations)
        successful_reconciliations = len([r for r in reconciliations if r["is_successful"]])
        failed_reconciliations = len([r for r in reconciliations if not r["is_successful"]])
        pending_reconciliations = len([r for r in reconciliations if r["status"] == "pending"])
        
        total_transactions_processed = sum(r["total_transactions"] for r in reconciliations)
        total_amount_processed = sum(r["total_amount"] for r in reconciliations)
        
        processing_times = [r["processing_time_seconds"] for r in reconciliations if r["processing_time_seconds"]]
        average_processing_time = sum(processing_times) / len(processing_times) if processing_times else None
        
        last_reconciliation = None
        completed_reconciliations = [r for r in reconciliations if r["completed_at"]]
        if completed_reconciliations:
            last_reconciliation = max(completed_reconciliations, key=lambda x: x["completed_at"])["completed_at"]
        
        return {
            "total_reconciliations": total_reconciliations,
            "successful_reconciliations": successful_reconciliations,
            "failed_reconciliations": failed_reconciliations,
            "pending_reconciliations": pending_reconciliations,
            "total_transactions_processed": total_transactions_processed,
            "total_amount_processed": total_amount_processed,
            "average_processing_time": average_processing_time,
            "last_reconciliation": last_reconciliation
        }
    
    def _mask_card_number(self, card_number: str) -> str:
        """Mask card number for security."""
        if len(card_number) < 8:
            return "*" * len(card_number)
        return card_number[:4] + "*" * (len(card_number) - 8) + card_number[-4:]


# Global mock database instance
mock_db = MockDatabase()
