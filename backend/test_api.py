"""
Test script to demonstrate the API with mock data.
Run this after starting the API server.
"""

import requests
import json
from datetime import datetime

# Base URL
BASE_URL = "http://localhost:8000"

def test_api() -> None:
    """Test the API endpoints with mock data."""
    
    print("Testing Transaction Reconciliation API with Mock Data")
    print("=" * 60)
    
    # Test 1: Health Check
    print("\n1. Testing Health Check...")
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=10)
        print(f"OK - Health Check: {response.status_code}")
        print(f"   Response: {response.json()}")
    except Exception as e:
        print(f"ERROR - Health Check Failed: {e}")
        return
    
    # Test 2: Get Root Info
    print("\n2. Testing Root Endpoint...")
    try:
        response = requests.get(f"{BASE_URL}/", timeout=10)
        print(f"OK - Root Endpoint: {response.status_code}")
        print(f"   Response: {response.json()}")
    except Exception as e:
        print(f"ERROR - Root Endpoint Failed: {e}")
    
    # Test 3: Get Sample Transactions
    print("\n3. Testing Get Transactions...")
    try:
        response = requests.get(f"{BASE_URL}/api/v1/transactions/", timeout=10)
        print(f"OK - Get Transactions: {response.status_code}")
        data = response.json()
        print(f"   Found {data['total']} transactions")
        if data['transactions']:
            print(f"   First transaction: {data['transactions'][0]['transaction_id']} - ${data['transactions'][0]['amount']}")
    except Exception as e:
        print(f"ERROR - Get Transactions Failed: {e}")
    
    # Test 4: Get Sample Issuers
    print("\n4. Testing Get Issuers...")
    try:
        response = requests.get(f"{BASE_URL}/api/v1/issuers/", timeout=10)
        print(f"OK Get Issuers: {response.status_code}")
        data = response.json()
        print(f"   Found {data['total']} issuers")
        if data['issuers']:
            print(f"   First issuer: {data['issuers'][0]['issuer_name']} ({data['issuers'][0]['issuer_code']})")
    except Exception as e:
        print(f"ERROR Get Issuers Failed: {e}")
    
    # Test 5: Get Sample Reconciliations
    print("\n5. Testing Get Reconciliations...")
    try:
        response = requests.get(f"{BASE_URL}/api/v1/reconciliations/", timeout=10)
        print(f"OK Get Reconciliations: {response.status_code}")
        data = response.json()
        print(f"   Found {data['total']} reconciliations")
        if data['reconciliations']:
            print(f"   First reconciliation: {data['reconciliations'][0]['reconciliation_id']} - {data['reconciliations'][0]['status']}")
    except Exception as e:
        print(f"ERROR Get Reconciliations Failed: {e}")
    
    # Test 6: Get Reconciliation Stats
    print("\n6. Testing Reconciliation Stats...")
    try:
        response = requests.get(f"{BASE_URL}/api/v1/reconciliations/stats/overview", timeout=10)
        print(f"OK Reconciliation Stats: {response.status_code}")
        data = response.json()
        print(f"   Total Reconciliations: {data['total_reconciliations']}")
        print(f"   Successful: {data['successful_reconciliations']}")
        print(f"   Failed: {data['failed_reconciliations']}")
        print(f"   Pending: {data['pending_reconciliations']}")
    except Exception as e:
        print(f"ERROR Reconciliation Stats Failed: {e}")
    
    # Test 7: Create New Transaction
    print("\n7. Testing Create Transaction...")
    try:
        new_transaction = {
            "transaction_id": "TXN-TEST-001",
            "issuer_id": "ISSUER-001",
            "card_number": "4111111111111111",
            "amount": 99.99,
            "currency": "USD",
            "transaction_type": "purchase",
            "transaction_status": "completed",
            "merchant_name": "Test Store",
            "merchant_category": "5999",
            "transaction_date": "2024-01-15T10:30:00Z"
        }
        
        response = requests.post(f"{BASE_URL}/api/v1/transactions/", json=new_transaction, timeout=10)
        print(f"OK Create Transaction: {response.status_code}")
        if response.status_code == 201:
            data = response.json()
            print(f"   Created: {data['transaction_id']} - ${data['amount']}")
            print(f"   Card masked: {data['card_number_masked']}")
    except Exception as e:
        print(f"ERROR Create Transaction Failed: {e}")
    
    # Test 8: Get Specific Transaction
    print("\n8. Testing Get Specific Transaction...")
    try:
        response = requests.get(f"{BASE_URL}/api/v1/transactions/TXN-001", timeout=10)
        print(f"OK Get Specific Transaction: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"   Transaction: {data['transaction_id']} - ${data['amount']}")
            print(f"   Status: {data['transaction_status']}")
            print(f"   Merchant: {data['merchant_name']}")
    except Exception as e:
        print(f"ERROR Get Specific Transaction Failed: {e}")
    
    print("\n" + "=" * 60)
    print("SUCCESS API Testing Complete!")
    print("\nINFO You can also test the API interactively at:")
    print(f"   INFO Swagger UI: {BASE_URL}/docs")
    print(f"   INFO ReDoc: {BASE_URL}/redoc")

if __name__ == "__main__":
    test_api()
