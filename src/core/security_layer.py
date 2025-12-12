"""
Security Layer - Encryption and security management
"""
import hashlib
import secrets
from typing import Any, Dict, Optional
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2
from src.utils.logger import get_logger
from src.utils.config_manager import get_config

logger = get_logger(__name__)


class SecurityLayer:
    """
    Security layer for encrypting sensitive data
    """
    
    def __init__(self, master_password: Optional[str] = None):
        self.logger = get_logger(__name__)
        self.encryption_enabled = get_config('system', 'security.encryption_enabled', True)
        
        # Generate or use provided key
        if master_password:
            self.key = self._derive_key(master_password)
        else:
            self.key = Fernet.generate_key()
        
        self.cipher = Fernet(self.key)
        
        self.logger.info("Security Layer initialized")
    
    def _derive_key(self, password: str, salt: Optional[bytes] = None) -> bytes:
        """Derive encryption key from password"""
        if salt is None:
            salt = b'orion_phi4_salt_'  # Static salt for consistency
        
        kdf = PBKDF2(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
        )
        
        key_material = kdf.derive(password.encode())
        # Fernet requires base64 encoded 32-byte key
        import base64
        return base64.urlsafe_b64encode(key_material)
    
    def encrypt(self, data: str) -> str:
        """
        Encrypt string data
        
        Args:
            data: String to encrypt
            
        Returns:
            Encrypted string (base64 encoded)
        """
        if not self.encryption_enabled:
            return data
        
        try:
            encrypted = self.cipher.encrypt(data.encode())
            return encrypted.decode()
        except Exception as e:
            self.logger.error(f"Encryption error: {e}")
            raise
    
    def decrypt(self, encrypted_data: str) -> str:
        """
        Decrypt string data
        
        Args:
            encrypted_data: Encrypted string to decrypt
            
        Returns:
            Decrypted string
        """
        if not self.encryption_enabled:
            return encrypted_data
        
        try:
            decrypted = self.cipher.decrypt(encrypted_data.encode())
            return decrypted.decode()
        except Exception as e:
            self.logger.error(f"Decryption error: {e}")
            raise
    
    def encrypt_dict(self, data: Dict[str, Any]) -> Dict[str, str]:
        """
        Encrypt dictionary values
        
        Args:
            data: Dictionary with string values
            
        Returns:
            Dictionary with encrypted values
        """
        encrypted = {}
        for key, value in data.items():
            if isinstance(value, str):
                encrypted[key] = self.encrypt(value)
            else:
                encrypted[key] = self.encrypt(str(value))
        return encrypted
    
    def decrypt_dict(self, encrypted_data: Dict[str, str]) -> Dict[str, str]:
        """
        Decrypt dictionary values
        
        Args:
            encrypted_data: Dictionary with encrypted values
            
        Returns:
            Dictionary with decrypted values
        """
        decrypted = {}
        for key, value in encrypted_data.items():
            decrypted[key] = self.decrypt(value)
        return decrypted
    
    def hash_data(self, data: str) -> str:
        """
        Create hash of data
        
        Args:
            data: String to hash
            
        Returns:
            Hex digest of hash
        """
        return hashlib.sha256(data.encode()).hexdigest()
    
    def generate_token(self, length: int = 32) -> str:
        """
        Generate secure random token
        
        Args:
            length: Length of token in bytes
            
        Returns:
            Hex token string
        """
        return secrets.token_hex(length)
    
    def verify_hash(self, data: str, hash_value: str) -> bool:
        """
        Verify data against hash
        
        Args:
            data: Original data
            hash_value: Hash to verify against
            
        Returns:
            True if hash matches
        """
        return self.hash_data(data) == hash_value
    
    def secure_compare(self, a: str, b: str) -> bool:
        """
        Constant-time string comparison
        
        Args:
            a: First string
            b: Second string
            
        Returns:
            True if strings match
        """
        return secrets.compare_digest(a, b)


class APIKeyManager:
    """
    Manages API keys and credentials securely
    """
    
    def __init__(self, security_layer: SecurityLayer):
        self.security = security_layer
        self.logger = get_logger(f"{__name__}.APIKeyManager")
        self.keys: Dict[str, str] = {}
    
    def store_key(self, name: str, key: str):
        """
        Store API key securely
        
        Args:
            name: Key identifier
            key: API key value
        """
        encrypted_key = self.security.encrypt(key)
        self.keys[name] = encrypted_key
        self.logger.info(f"Stored API key: {name}")
    
    def retrieve_key(self, name: str) -> Optional[str]:
        """
        Retrieve and decrypt API key
        
        Args:
            name: Key identifier
            
        Returns:
            Decrypted API key or None
        """
        encrypted_key = self.keys.get(name)
        if encrypted_key:
            return self.security.decrypt(encrypted_key)
        return None
    
    def delete_key(self, name: str):
        """Delete API key"""
        if name in self.keys:
            del self.keys[name]
            self.logger.info(f"Deleted API key: {name}")
    
    def list_keys(self) -> list:
        """List all stored key names"""
        return list(self.keys.keys())


# Global security layer instance
_security_layer = None
_api_key_manager = None


def get_security_layer(master_password: Optional[str] = None) -> SecurityLayer:
    """Get or create global security layer instance"""
    global _security_layer
    if _security_layer is None:
        _security_layer = SecurityLayer(master_password)
    return _security_layer


def get_api_key_manager() -> APIKeyManager:
    """Get or create global API key manager instance"""
    global _api_key_manager
    if _api_key_manager is None:
        security = get_security_layer()
        _api_key_manager = APIKeyManager(security)
    return _api_key_manager
