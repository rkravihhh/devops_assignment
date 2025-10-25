"""
Debug script to test the application components.
"""

from fastapi import FastAPI
from fastapi.testclient import TestClient

# Test basic FastAPI
app = FastAPI()

@app.get("/")
def read_root() -> None:
    return {"message": "Hello World"}

@app.get("/health")
def health() -> None:
    return {"status": "healthy"}

if __name__ == "__main__":
    client = TestClient(app)
    print("Testing basic FastAPI:")
    print("Root:", client.get("/").json())
    print("Health:", client.get("/health").json())
    
    print("\nTesting our app components:")
    try:
        from app.core.config import settings
        print("OK - Config imported successfully")
    except Exception as e:
        print(f"ERROR - Config import failed: {e}")
    
    try:
        from app.core.database import get_db, init_db
        print("OK - Database imported successfully")
    except Exception as e:
        print(f"ERROR - Database import failed: {e}")
    
    try:
        from app.api.v1.api import api_router
        print("OK - API router imported successfully")
    except Exception as e:
        print(f"ERROR - API router import failed: {e}")
    
    try:
        from app.core.middleware import LoggingMiddleware, SecurityHeadersMiddleware
        print("OK - Middleware imported successfully")
    except Exception as e:
        print(f"ERROR - Middleware import failed: {e}")
    
    try:
        from app.core.exceptions import setup_exception_handlers
        print("OK - Exceptions imported successfully")
    except Exception as e:
        print(f"ERROR - Exceptions import failed: {e}")
    
    print("\nTesting main app import:")
    try:
        from main import app as main_app
        print("OK - Main app imported successfully")
        
        # Test the main app
        client = TestClient(main_app)
        print("Root:", client.get("/").json())
        print("Health:", client.get("/health").json())
        
    except Exception as e:
        print(f"ERROR - Main app import failed: {e}")
        import traceback
        traceback.print_exc()
