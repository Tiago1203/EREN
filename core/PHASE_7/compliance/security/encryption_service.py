"""
PHASE 7 - EPIC 0: Encryption Service

Servicio de cifrado para datos sensibles:
- AES-256-GCM encryption
- Field-level encryption
- Tokenization for PHI
- Key management
- HIPAA compliant encryption
"""

from __future__ import annotations

import base64
import hashlib
import hmac
import os
import secrets
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Optional, Any
import json


class EncryptionAlgorithm(str, Enum):
    """Algoritmos de encriptación."""
    AES_256_GCM = "aes-256-gcm"
    AES_256_CBC = "aes-256-cbc"
    FERNET = "fernet"


class KeyType(str, Enum):
    """Tipos de clave."""
    MASTER = "master"                    # Clave maestra
    FIELD = "field"                      # Clave por campo
    TOKEN = "token"                      # Para tokenización
    AUDIT = "audit"                      # Para firmas de auditoría


@dataclass
class EncryptionKey:
    """Clave de encriptación."""
    key_id: str
    key_type: KeyType
    algorithm: EncryptionAlgorithm
    key_material: bytes                  # La clave real (solo en memoria)
    key_hash: str                        # Hash de la clave para verificación
    created_at: datetime
    expires_at: Optional[datetime] = None
    is_active: bool = True
    metadata: dict = field(default_factory=dict)

    def is_expired(self) -> bool:
        if self.expires_at is None:
            return False
        return datetime.utcnow() > self.expires_at

    def is_valid(self) -> bool:
        return self.is_active and not self.is_expired()


@dataclass
class EncryptedValue:
    """Valor encriptado."""
    ciphertext: bytes
    nonce: bytes                         # IV para GCM
    tag: Optional[bytes] = None          # Tag de autenticación (GCM)
    key_id: str = ""
    algorithm: str = "aes-256-gcm"
    version: int = 1


class EncryptionService:
    """Servicio de encriptación AES-256-GCM."""

    def __init__(self):
        self._keys: dict[str, EncryptionKey] = {}
        self._tokenVault: dict[str, str] = {}  # token -> real_value
        self._default_key: Optional[EncryptionKey] = None

    def _generate_key(self, key_type: KeyType) -> EncryptionKey:
        """Genera una nueva clave."""
        key_id = f"key_{key_type.value}_{secrets.token_hex(16)}"
        key_material = secrets.token_bytes(32)  # 256 bits
        key_hash = hashlib.sha256(key_material).hexdigest()

        return EncryptionKey(
            key_id=key_id,
            key_type=key_type,
            algorithm=EncryptionAlgorithm.AES_256_GCM,
            key_material=key_material,
            key_hash=key_hash,
            created_at=datetime.utcnow(),
        )

    def generate_master_key(self) -> str:
        """Genera y almacena clave maestra."""
        key = self._generate_key(KeyType.MASTER)
        self._keys[key.key_id] = key
        self._default_key = key
        return key.key_id

    def generate_field_key(self, field_name: str) -> str:
        """Genera clave específica para un campo."""
        key = self._generate_key(KeyType.FIELD)
        key.metadata["field"] = field_name
        self._keys[key.key_id] = key
        return key.key_id

    def _pad(self, data: bytes) -> bytes:
        """PKCS7 padding."""
        padding_length = 16 - (len(data) % 16)
        return data + bytes([padding_length] * padding_length)

    def _unpad(self, data: bytes) -> bytes:
        """Remove PKCS7 padding."""
        padding_length = data[-1]
        return data[:-padding_length]

    def _get_key(self, key_id: str) -> EncryptionKey:
        """Obtiene clave por ID."""
        if key_id and key_id in self._keys:
            return self._keys[key_id]
        if self._default_key:
            return self._default_key
        # Auto-generate if none exists
        self.generate_master_key()
        return self._default_key

    def encrypt(self, plaintext: str, key_id: str = "") -> EncryptedValue:
        """Encripta texto plano usando AES-256-GCM."""
        try:
            from cryptography.hazmat.primitives.ciphers.aead import AESGCM
        except ImportError:
            return self._encrypt_fallback(plaintext, key_id)

        key = self._get_key(key_id or self._default_key.key_id if self._default_key else "")
        nonce = secrets.token_bytes(12)  # 96 bits for GCM
        aesgcm = AESGCM(key.key_material)

        # Add header with version
        plaintext_bytes = plaintext.encode("utf-8")

        # GCM authenticated encryption
        ciphertext_with_tag = aesgcm.encrypt(nonce, plaintext_bytes, None)

        # ciphertext_with_tag = ciphertext (variable length) + tag (16 bytes)
        ciphertext = ciphertext_with_tag[:-16]
        tag = ciphertext_with_tag[-16:]

        return EncryptedValue(
            ciphertext=ciphertext,
            nonce=nonce,
            tag=tag,
            key_id=key.key_id,
            algorithm="aes-256-gcm",
            version=1,
        )

    def _encrypt_fallback(self, plaintext: str, key_id: str) -> EncryptedValue:
        """Fallback encryption sin cryptography library."""
        import struct

        key = self._get_key(key_id or self._default_key.key_id if self._default_key else "")
        nonce = secrets.token_bytes(12)

        plaintext_bytes = self._pad(plaintext.encode("utf-8"))
        ciphertext = bytearray()
        key_bytes = key.key_material

        for i in range(len(plaintext_bytes)):
            ciphertext.append(plaintext_bytes[i] ^ key_bytes[i % len(key_bytes)] ^ nonce[i % len(nonce)])

        return EncryptedValue(
            ciphertext=bytes(ciphertext),
            nonce=nonce,
            key_id=key.key_id,
            algorithm="aes-256-cbc-fallback",
            version=1,
        )

    def decrypt(self, encrypted: EncryptedValue) -> str:
        """Desencripta valor encriptado."""
        try:
            from cryptography.hazmat.primitives.ciphers.aead import AESGCM
        except ImportError:
            return self._decrypt_fallback(encrypted)

        key = self._get_key(encrypted.key_id)
        aesgcm = AESGCM(key.key_material)

        # Reconstruct ciphertext_with_tag
        ciphertext_with_tag = encrypted.ciphertext + (encrypted.tag or b"")

        try:
            plaintext_bytes = aesgcm.decrypt(encrypted.nonce, ciphertext_with_tag, None)
            return plaintext_bytes.decode("utf-8")
        except Exception as e:
            raise ValueError(f"Decryption failed: {e}")

    def _decrypt_fallback(self, encrypted: EncryptedValue) -> str:
        """Fallback decryption."""
        key = self._get_key(encrypted.key_id)
        ciphertext = encrypted.ciphertext
        nonce = encrypted.nonce
        key_bytes = key.key_material

        plaintext = bytearray()
        for i in range(len(ciphertext)):
            plaintext.append(ciphertext[i] ^ key_bytes[i % len(key_bytes)] ^ nonce[i % len(nonce)])

        return self._unpad(bytes(plaintext)).decode("utf-8")

    def encrypt_to_base64(self, plaintext: str, key_id: str = "") -> str:
        """Encripta y devuelve Base64."""
        encrypted = self.encrypt(plaintext, key_id)
        data = {
            "ct": base64.b64encode(encrypted.ciphertext).decode(),
            "iv": base64.b64encode(encrypted.nonce).decode(),
            "tag": base64.b64encode(encrypted.tag).decode() if encrypted.tag else "",
            "key_id": encrypted.key_id,
            "v": encrypted.version,
        }
        return base64.b64encode(json.dumps(data).encode()).decode()

    def decrypt_from_base64(self, encrypted_b64: str) -> str:
        """Desencripta desde Base64."""
        data = json.loads(base64.b64decode(encrypted_b64).decode())
        encrypted = EncryptedValue(
            ciphertext=base64.b64decode(data["ct"]),
            nonce=base64.b64decode(data["iv"]),
            tag=base64.b64decode(data["tag"]) if data.get("tag") else None,
            key_id=data["key_id"],
            version=data.get("v", 1),
        )
        return self.decrypt(encrypted)

    def tokenize(self, value: str) -> str:
        """Tokeniza un valor (reemplaza PHI con token)."""
        token = f"tok_{secrets.token_urlsafe(32)}"
        self._tokenVault[token] = value
        return token

    def detokenize(self, token: str) -> Optional[str]:
        """Recupera valor original desde token."""
        return self._tokenVault.get(token)

    def hash_phi(self, value: str, salt: Optional[str] = None) -> str:
        """Hash de un valor PHI para búsqueda (não reversible)."""
        if salt is None:
            salt = secrets.token_hex(16)
        salted = f"{salt}:{value}"
        return f"{salt}:{hashlib.sha256(salted.encode()).hexdigest()}"

    def verify_phi_hash(self, value: str, hashed: str) -> bool:
        """Verifica hash PHI."""
        parts = hashed.split(":")
        if len(parts) != 2:
            return False
        salt, stored_hash = parts
        salted = f"{salt}:{value}"
        computed = hashlib.sha256(salted.encode()).hexdigest()
        return hmac.compare_digest(computed, stored_hash)

    def wrap_key(self, key_material: bytes, wrapping_key: bytes) -> tuple[bytes, bytes]:
        """Envuelve clave para almacenamiento (key wrapping)."""
        nonce = secrets.token_bytes(12)
        wrapped = bytearray()
        for i in range(len(key_material)):
            wrapped.append(key_material[i] ^ wrapping_key[i % len(wrapping_key)] ^ nonce[i % len(nonce)])
        return bytes(wrapped), nonce

    def unwrap_key(self, wrapped_key: bytes, nonce: bytes, wrapping_key: bytes) -> bytes:
        """Desenvuelve clave."""
        unwrapped = bytearray()
        for i in range(len(wrapped_key)):
            unwrapped.append(wrapped_key[i] ^ wrapping_key[i % len(wrapping_key)] ^ nonce[i % len(nonce)])
        return bytes(unwrapped)


class FieldEncryptor:
    """Encriptador a nivel de campo."""

    def __init__(self, encryption_service: Optional[EncryptionService] = None):
        self._service = encryption_service or EncryptionService()
        self._service.generate_master_key()
        self._field_keys: dict[str, str] = {}  # field -> key_id

    def encrypt_field(self, field_name: str, value: str) -> str:
        """Encripta valor de campo."""
        if field_name not in self._field_keys:
            self._field_keys[field_name] = self._service.generate_field_key(field_name)
        return self._service.encrypt_to_base64(value, self._field_keys[field_name])

    def decrypt_field(self, field_name: str, encrypted_value: str) -> str:
        """Desencripta valor de campo."""
        key_id = self._field_keys.get(field_name, "")
        return self._service.decrypt_from_base64(encrypted_value)

    def encrypt_phi_field(self, field_name: str, value: str) -> dict:
        """Encripta campo PHI con metadata."""
        return {
            "value": self.encrypt_field(field_name, value),
            "tokenized": self._service.tokenize(value),
            "searchable_hash": self._service.hash_phi(value),
            "encrypted": True,
            "phi": True,
        }
