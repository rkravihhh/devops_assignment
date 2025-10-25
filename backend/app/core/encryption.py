"""
Data encryption utilities for PCI DSS Level 1 compliance.
"""

import hashlib
import hmac
import secrets
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import base64
import os
from typing import Optional, Dict, Any
import structlog

logger = structlog.get_logger()


class PCIEncryption:
    """PCI DSS Level 1 compliant encryption utilities."""
    
    def __init__(self, secret_key: str) -> None:
        self.secret_key = secret_key.encode()
        self._fernet: Optional[Fernet] = None
    
    @property
    def fernet(self) -> Fernet:
        """Get Fernet encryption instance."""
        if self._fernet is None:
            # Derive key from secret using PBKDF2
            kdf = PBKDF2HMAC(
                algorithm=hashes.SHA256(),
                length=32,
                salt=b'pci_salt_2024',  # In production, use random salt
                iterations=100000,
            )
            key = base64.urlsafe_b64encode(kdf.derive(self.secret_key))
            self._fernet = Fernet(key)
        assert self._fernet is not None
        return self._fernet
    
    def encrypt_sensitive_data(self, data: str) -> str:
        """Encrypt sensitive data for PCI compliance."""
        try:
            encrypted_data = self.fernet.encrypt(data.encode())
            return base64.urlsafe_b64encode(encrypted_data).decode()
        except Exception as e:
            logger.error("Encryption failed", error=str(e))
            raise ValueError("Failed to encrypt sensitive data")
    
    def decrypt_sensitive_data(self, encrypted_data: str) -> str:
        """Decrypt sensitive data."""
        try:
            decoded_data = base64.urlsafe_b64decode(encrypted_data.encode())
            decrypted_data = self.fernet.decrypt(decoded_data)
            return decrypted_data.decode()
        except Exception as e:
            logger.error("Decryption failed", error=str(e))
            raise ValueError("Failed to decrypt sensitive data")
    
    def hash_card_number(self, card_number: str) -> str:
        """Create one-way hash of card number for PCI compliance."""
        # Use HMAC with secret key for additional security
        hash_obj = hmac.new(
            self.secret_key,
            card_number.encode(),
            hashlib.sha256
        )
        return hash_obj.hexdigest()
    
    def mask_card_number(self, card_number: str) -> str:
        """Mask card number for display (show first 6, last 4)."""
        if len(card_number) < 10:
            return "*" * len(card_number)
        
        return f"{card_number[:6]}{'*' * (len(card_number) - 10)}{card_number[-4:]}"
    
    def generate_secure_token(self, length: int = 32) -> str:
        """Generate cryptographically secure random token."""
        return secrets.token_urlsafe(length)
    
    def create_hmac_signature(self, data: str, timestamp: str) -> str:
        """Create HMAC signature for data integrity."""
        message = f"{data}:{timestamp}"
        signature = hmac.new(
            self.secret_key,
            message.encode(),
            hashlib.sha256
        ).hexdigest()
        return signature
    
    def verify_hmac_signature(self, data: str, timestamp: str, signature: str) -> bool:
        """Verify HMAC signature."""
        expected_signature = self.create_hmac_signature(data, timestamp)
        return hmac.compare_digest(signature, expected_signature)


class TransactionDataProtection:
    """Transaction data protection for PCI DSS compliance."""
    
    def __init__(self, encryption: PCIEncryption) -> None:
        self.encryption = encryption
    
    def protect_transaction_data(self, transaction_data: Dict[str, Any]) -> Dict[str, Any]:
        """Protect sensitive transaction data."""
        protected_data = transaction_data.copy()
        
        # Hash card number for storage
        if 'card_number' in protected_data:
            card_number = protected_data['card_number']
            protected_data['card_number_hash'] = self.encryption.hash_card_number(card_number)
            protected_data['card_number_masked'] = self.encryption.mask_card_number(card_number)
            # Remove original card number
            del protected_data['card_number']
        
        # Encrypt sensitive metadata
        if 'metadata' in protected_data and protected_data['metadata']:
            sensitive_metadata = protected_data['metadata']
            if isinstance(sensitive_metadata, dict):
                # Encrypt sensitive fields in metadata
                for key, value in sensitive_metadata.items():
                    if key.lower() in ['cvv', 'pin', 'ssn', 'account_number']:
                        protected_data['metadata'][key] = self.encryption.encrypt_sensitive_data(str(value))
        
        return protected_data
    
    def restore_transaction_data(self, protected_data: Dict[str, Any]) -> Dict[str, Any]:
        """Restore transaction data for processing."""
        restored_data = protected_data.copy()
        
        # Decrypt sensitive metadata
        if 'metadata' in restored_data and restored_data['metadata']:
            sensitive_metadata = restored_data['metadata']
            if isinstance(sensitive_metadata, dict):
                for key, value in sensitive_metadata.items():
                    if key.lower() in ['cvv', 'pin', 'ssn', 'account_number']:
                        try:
                            restored_data['metadata'][key] = self.encryption.decrypt_sensitive_data(str(value))
                        except ValueError:
                            # If decryption fails, keep encrypted value
                            logger.warning("Failed to decrypt sensitive field", field=key)
        
        return restored_data


# Global encryption instance
def get_encryption() -> PCIEncryption:
    """Get encryption instance."""
    from app.core.config import settings
    return PCIEncryption(settings.SECRET_KEY)


def get_data_protection() -> TransactionDataProtection:
    """Get data protection instance."""
    return TransactionDataProtection(get_encryption())
