"""
Tests for transaction endpoints.
"""

import pytest
from fastapi.testclient import TestClient

from main import app

client = TestClient(app)


def test_create_transaction() -> None:
    """Test creating a transaction."""
    transaction_data = {
        "transaction_id": "TXN-001",
        "issuer_id": "ISSUER-001",
        "card_number": "4111111111111111",
        "amount": 100.50,
        "currency": "USD",
        "transaction_type": "purchase",
        "transaction_status": "completed",
        "merchant_name": "Test Merchant",
        "transaction_date": "2024-01-01T10:00:00Z"
    }
    
    response = client.post("/api/v1/transactions/", json=transaction_data)
    assert response.status_code == 201
    data = response.json()
    assert data["transaction_id"] == "TXN-001"
    assert data["card_number_masked"] is not None
    assert data["amount"] == 100.50


def test_get_transaction() -> None:
    """Test getting a transaction."""
    # First create a transaction
    transaction_data = {
        "transaction_id": "TXN-002",
        "issuer_id": "ISSUER-001",
        "card_number": "4111111111111111",
        "amount": 200.00,
        "currency": "USD",
        "transaction_type": "purchase",
        "transaction_status": "completed",
        "merchant_name": "Test Merchant",
        "transaction_date": "2024-01-01T10:00:00Z"
    }
    
    create_response = client.post("/api/v1/transactions/", json=transaction_data)
    assert create_response.status_code == 201
    
    # Then get it
    response = client.get(f"/api/v1/transactions/{transaction_data['transaction_id']}")
    assert response.status_code == 200
    data = response.json()
    assert data["transaction_id"] == "TXN-002"


def test_search_transactions() -> None:
    """Test searching transactions."""
    response = client.get("/api/v1/transactions/")
    assert response.status_code == 200
    data = response.json()
    assert "transactions" in data
    assert "total" in data
    assert "page" in data
    assert "size" in data
