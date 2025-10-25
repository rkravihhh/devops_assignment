"""
Debug script to test the mock database.
"""

from app.core.mock_database import mock_db
from app.services.transaction_service import TransactionService
from app.schemas.transaction import TransactionSearchRequest

def test_mock_database() -> None:
    """Test the mock database functionality."""
    print("Testing Mock Database...")
    
    # Test 1: Check if mock database has data
    print(f"Transactions: {len(mock_db.data['transactions'])}")
    print(f"Issuers: {len(mock_db.data['issuers'])}")
    print(f"Reconciliations: {len(mock_db.data['reconciliations'])}")
    
    # Test 2: Test search method
    try:
        filters = {}
        transactions = mock_db.search_transactions(filters)
        print(f"Search transactions result: {len(transactions)} transactions found")
        if transactions:
            print(f"First transaction: {transactions[0]['transaction_id']}")
    except Exception as e:
        print(f"Search transactions failed: {e}")
        import traceback
        traceback.print_exc()
    
    # Test 3: Test transaction service
    try:
        import asyncio
        async def test_service() -> None:
            service = TransactionService(mock_db)
            search_request = TransactionSearchRequest(page=1, size=20)
            result = await service.search_transactions(search_request)
            print(f"Transaction service result: {result.total} transactions")
        
        asyncio.run(test_service())
    except Exception as e:
        print(f"Transaction service failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_mock_database()
