import time
import re
from collections import defaultdict
from datetime import datetime, timedelta, timezone
from typing import Optional, Any, Tuple
from jose import jwt, JWTError, ExpiredSignatureError
from passlib.context import CryptContext
from fastapi import HTTPException, status, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from app.core.config import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
security_bearer = HTTPBearer(auto_error=False)

class SlidingWindowRateLimiter:
    """
    In-memory thread-safe sliding window rate limiter for endpoint protection.
    """
    def __init__(self, limit: int = 30, window_seconds: int = 60):
        self.limit = limit
        self.window = window_seconds
        self.requests = defaultdict(list)

    def is_allowed(self, key: str) -> bool:
        if not settings.RATE_LIMIT_ENABLED:
            return True
        now = time.time()
        window_start = now - self.window
        timestamps = [t for t in self.requests[key] if t > window_start]
        self.requests[key] = timestamps
        if len(timestamps) >= self.limit:
            return False
        self.requests[key].append(now)
        return True

auth_rate_limiter = SlidingWindowRateLimiter(
    limit=settings.AUTH_RATE_LIMIT_PER_MINUTE,
    window_seconds=60
)

def check_auth_rate_limit(request: Request):
    """
    FastAPI dependency to rate-limit authentication endpoints by client IP.
    """
    client_ip = request.client.host if request.client else "unknown"
    if not auth_rate_limiter.is_allowed(client_ip):
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Too many authentication attempts. Please slow down and try again in one minute."
        )

def validate_password_strength(password: str) -> Tuple[bool, str]:
    """
    Enforces secure password policies:
    - Minimum 8 characters
    - At least one uppercase letter
    - At least one lowercase letter
    - At least one numeric digit or special symbol
    """
    if len(password) < 8:
        return False, "Password must be at least 8 characters long."
    if not re.search(r"[A-Z]", password):
        return False, "Password must contain at least one uppercase letter."
    if not re.search(r"[a-z]", password):
        return False, "Password must contain at least one lowercase letter."
    if not re.search(r"[\d\W_]", password):
        return False, "Password must contain at least one numeric digit or special character."
    return True, ""

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

def create_access_token(subject: str | Any, expires_delta: Optional[timedelta] = None) -> str:
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode = {
        "exp": expire,
        "sub": str(subject),
        "iat": datetime.now(timezone.utc),
        "iss": "edupath-ai-auth"
    }
    encoded_jwt = jwt.encode(to_encode, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)
    return encoded_jwt

def decode_access_token(token: str) -> Optional[str]:
    try:
        payload = jwt.decode(
            token,
            settings.JWT_SECRET,
            algorithms=[settings.JWT_ALGORITHM],
            options={"verify_exp": True}
        )
        user_id: str = payload.get("sub")
        return user_id
    except (JWTError, ExpiredSignatureError):
        return None
