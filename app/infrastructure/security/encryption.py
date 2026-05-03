import os
import base64
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from typing import Optional

class FieldEncryptor:
    """
    Standard AES-GCM-256 Encryptor for application-level field encryption.
    Designed for protecting PII (Personally Identifiable Information) at rest.
    """
    def __init__(self, master_key: str):
        # In production, keys should be derived from HSM/KMS.
        # Here we ensure we have a valid 32-byte key (256 bits).
        if len(master_key) < 32:
             # Basic derivation if key is too short (Not for prod)
             salt = b'sblc-ledger-salt'
             kdf = PBKDF2HMAC(
                algorithm=hashes.SHA256(),
                length=32,
                salt=salt,
                iterations=100000,
             )
             self.key = kdf.derive(master_key.encode())
        else:
             self.key = master_key.encode()[:32]
        
        self.aesgcm = AESGCM(self.key)

    def encrypt(self, data: str) -> str:
        if not data:
            return ""
        nonce = os.urandom(12) # 96-bit nonce for GCM
        ciphertext = self.aesgcm.encrypt(nonce, data.encode(), None)
        # Encode as base64 for database storage
        return base64.b64encode(nonce + ciphertext).decode('utf-8')

    def decrypt(self, encrypted_base64: str) -> Optional[str]:
        if not encrypted_base64:
            return None
        try:
            raw_data = base64.b64decode(encrypted_base64)
            nonce = raw_data[:12]
            ciphertext = raw_data[12:]
            decrypted = self.aesgcm.decrypt(nonce, ciphertext, None)
            return decrypted.decode('utf-8')
        except Exception as e:
            # In a real auditor-monitored system, this would trigger a security alert
            print(f"Decryption Error: {e}")
            return None

# Singleton instance placeholder (initialized in app startup)
_encryptor: Optional[FieldEncryptor] = None

def get_encryptor(key: str = "SECURE_DEFAULT_KEY_DO_NOT_USE_IN_PROD") -> FieldEncryptor:
    global _encryptor
    if _encryptor is None:
        _encryptor = FieldEncryptor(key)
    return _encryptor
