# app/core/auth_utils.py
import hashlib
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    """
    Hash a password using SHA256 + bcrypt to avoid bcrypt's 72-byte limit.
    """
    sha256_hash = hashlib.sha256(password.encode('utf-8')).hexdigest()
    return pwd_context.hash(sha256_hash)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify a password against the hashed version.
    """
    sha256_hash = hashlib.sha256(plain_password.encode('utf-8')).hexdigest()
    return pwd_context.verify(sha256_hash, hashed_password)