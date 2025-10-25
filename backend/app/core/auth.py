"""
Authentication and authorization for PCI DSS Level 1 compliance.
"""

import hashlib
import hmac
import time
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from fastapi import HTTPException, Depends, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError, jwt
import structlog

from app.core.config import settings

logger = structlog.get_logger()
security = HTTPBearer()


class PCIAuthentication:
    """PCI DSS Level 1 compliant authentication."""
    
    def __init__(self) -> None:
        self.api_keys: Dict[str, Dict[str, Any]] = {
            # In production, these should be stored securely (AWS Secrets Manager, etc.)
            "dev-key-123": {
                "issuer_id": "issuer-001",
                "permissions": ["read", "write"],
                "rate_limit": 1000,
                "expires": None
            },
            "prod-key-456": {
                "issuer_id": "issuer-002", 
                "permissions": ["read"],
                "rate_limit": 500,
                "expires": datetime(2024, 12, 31)
            }
        }
    
    def validate_api_key(self, api_key: str) -> Optional[Dict[str, Any]]:
        """Validate API key for PCI compliance."""
        if api_key not in self.api_keys:
            logger.warning("Invalid API key attempted", api_key=api_key[:8] + "...")
            return None
        
        key_info = self.api_keys[api_key]
        
        # Check expiration
        if key_info.get("expires") and datetime.now() > key_info["expires"]:
            logger.warning("Expired API key attempted", api_key=api_key[:8] + "...")
            return None
        
        logger.info("API key validated", issuer_id=key_info.get("issuer_id"))
        return key_info
    
    def create_jwt_token(self, issuer_id: str, permissions: list) -> str:
        """Create JWT token for authenticated sessions."""
        now = datetime.utcnow()
        payload = {
            "iss": settings.JWT_ISSUER,
            "aud": settings.JWT_AUDIENCE,
            "sub": issuer_id,
            "iat": now,
            "exp": now + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES),
            "permissions": permissions,
            "pci_compliant": True
        }
        
        token: str = jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.JWT_ALGORITHM)
        logger.info("JWT token created", issuer_id=issuer_id)
        return token
    
    def validate_jwt_token(self, token: str) -> Optional[Dict[str, Any]]:
        """Validate JWT token."""
        try:
            payload = jwt.decode(
                token, 
                settings.SECRET_KEY, 
                algorithms=[settings.JWT_ALGORITHM],
                audience=settings.JWT_AUDIENCE,
                issuer=settings.JWT_ISSUER
            )
            
            # Check PCI compliance flag
            if not payload.get("pci_compliant"):
                raise HTTPException(status_code=403, detail="Token not PCI compliant")
            
            return payload
            
        except JWTError as e:
            logger.warning("JWT validation failed", error=str(e))
            raise HTTPException(status_code=401, detail="Invalid token")


# Global authentication instance
auth = PCIAuthentication()


async def get_current_user_api_key(request: Request) -> Dict[str, Any]:
    """Get current user from API key authentication."""
    if not settings.ENABLE_API_KEY_AUTH:
        raise HTTPException(status_code=401, detail="API key authentication disabled")
    
    api_key = request.headers.get(settings.API_KEY_HEADER)
    if not api_key:
        raise HTTPException(status_code=401, detail="API key required")
    
    user_info = auth.validate_api_key(api_key)
    if not user_info:
        raise HTTPException(status_code=401, detail="Invalid API key")
    
    return user_info


async def get_current_user_jwt(credentials: HTTPAuthorizationCredentials = Depends(security)) -> Dict[str, Any]:
    """Get current user from JWT authentication."""
    if not settings.ENABLE_JWT_AUTH:
        raise HTTPException(status_code=401, detail="JWT authentication disabled")
    
    result = auth.validate_jwt_token(credentials.credentials)
    if result is None:
        raise HTTPException(status_code=401, detail="Invalid token")
    return result


def require_permission(permission: str) -> Any:
    """Require specific permission for endpoint access."""
    def permission_checker(user: Dict[str, Any] = Depends(get_current_user_api_key)) -> Dict[str, Any]:
        if permission not in user.get("permissions", []):
            logger.warning(
                "Permission denied",
                required_permission=permission,
                user_permissions=user.get("permissions", [])
            )
            raise HTTPException(status_code=403, detail=f"Permission '{permission}' required")
        return user
    
    return permission_checker


def require_issuer_access() -> Any:
    """Require access to specific issuer data."""
    def issuer_checker(user: Dict[str, Any] = Depends(get_current_user_api_key)) -> Dict[str, Any]:
        issuer_id = user.get("issuer_id")
        if not issuer_id:
            raise HTTPException(status_code=403, detail="Issuer access required")
        return user
    
    return issuer_checker


class PCIAuditLogger:
    """PCI DSS audit logging for transaction access."""
    
    @staticmethod
    def log_transaction_access(
        user_id: str,
        action: str,
        transaction_id: Optional[str] = None,
        issuer_id: Optional[str] = None,
        success: bool = True,
        details: Optional[Dict[str, Any]] = None
    ) -> None:
        """Log transaction access for PCI compliance."""
        audit_data = {
            "event_type": "transaction_access",
            "user_id": user_id,
            "action": action,
            "transaction_id": transaction_id,
            "issuer_id": issuer_id,
            "success": success,
            "timestamp": datetime.utcnow().isoformat(),
            "details": details or {}
        }
        
        logger.info("PCI audit log", **audit_data)
