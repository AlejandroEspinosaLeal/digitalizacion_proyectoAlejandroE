from datetime import datetime, timedelta
from typing import Any, Union
from jose import jwt
import bcrypt
from src.backend.core.config import settings

def create_access_token(subject: Union[str, Any]) -> str:
    """Synchronously encodes a subject string into a JSON Web Token verified by HS256."""
    expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode = {"exp": expire, "sub": str(subject)}
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Validates the input password against the raw bcrypt DB hash string."""
    return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))

def get_password_hash(password: str) -> str:
    """Transforms a raw string password securely into a salted bcrypt hash."""
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')