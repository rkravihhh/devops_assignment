"""
Main API router for v1 endpoints.
"""

from fastapi import APIRouter
from app.api.v1.endpoints import transactions, issuers, reconciliations, health

api_router = APIRouter()

# Include all endpoint routers
api_router.include_router(health.router, prefix="/health", tags=["Health"])
api_router.include_router(transactions.router, prefix="/transactions", tags=["Transactions"])
api_router.include_router(issuers.router, prefix="/issuers", tags=["Issuers"])
api_router.include_router(reconciliations.router, prefix="/reconciliations", tags=["Reconciliations"])
