"""
Startup script for the Transaction Reconciliation API with mock database.
"""

import uvicorn
import sys
import os

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

if __name__ == "__main__":
    print(" Starting Transaction Reconciliation API with Mock Database")
    print("=" * 60)
    print(" Mock data includes:")
    print("   • 2 sample issuers (Chase Bank, Bank of America)")
    print("   • 2 sample transactions")
    print("   • 1 sample reconciliation")
    print("=" * 60)
    print(" API will be available at:")
    print("   • Main API: http://localhost:8000")
    print("   • Health Check: http://localhost:8000/health")
    print("   • API Docs: http://localhost:8000/docs")
    print("   • ReDoc: http://localhost:8000/redoc")
    print("=" * 60)
    print(" To test the API, run: python test_api.py")
    print("=" * 60)
    
    # Start the server
    uvicorn.run(
        "main:app",
        host="127.0.0.1",  # Changed from 0.0.0.0 for security
        port=8000,
        reload=True,
        log_level="info"
    )
