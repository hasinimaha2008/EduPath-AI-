import os
import time
import re
import secrets
import logging
from collections import defaultdict
from datetime import datetime, timedelta, timezone
from typing import Optional, Any, Tuple
from jose import jwt, JWTError, ExpiredSignatureError
from passlib.context import CryptContext
from fastapi import HTTPException, status, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from app.core.config import settings

logger = logging.getLogger("edupath.security")
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
security_bearer = HTTPBearer(auto_error=False)

class RateLimiter:
    """
    Hybrid distributed rate limiter:
    - Primary: Shared Redis sorted sets (supports multi-worker and multi-container deployments).
    - Fallback: Local thread-safe in-memory sliding window when Redis is unconfigured or unreachable.
    """
    def __init__(self, limit: int = 30, window_seconds: int = 60, prefix: str = "ratelimit"):
        self.limit = limit
        self.window = window_seconds
        self.prefix = prefix
        self._memory_requests = defaultdict(list)
        self._redis_client = None
        self._redis_tested = False
        self._redis_available = False
        self._last_retry_time = 0.0
        self._retry_interval = 30.0  # Seconds before retrying Redis connection

    def _get_redis(self):
        now = time.time()
        if self._redis_available and self._redis_client:
            return self._redis_client

        if self._redis_tested and not self._redis_available:
            if now - self._last_retry_time < self._retry_interval:
                return None

        self._redis_tested = True
        self._last_retry_time = now
        if settings.REDIS_URL:
            try:
                import redis
                client = redis.from_url(
                    settings.REDIS_URL,
                    decode_responses=True,
                    socket_timeout=1.0,
                    socket_connect_timeout=1.0
                )
                client.ping()
                self._redis_client = client
                self._redis_available = True
                logger.info(f"RateLimiter connected to distributed Redis at {settings.REDIS_URL}")
                return self._redis_client
            except Exception as e:
                logger.warning(f"Redis unavailable ({e}); falling back to local in-memory rate limiting.")
                self._redis_available = False
                self._redis_client = None
        else:
            self._redis_available = False
            self._redis_client = None
        return None

    def is_allowed(self, key: str, custom_limit: Optional[int] = None) -> bool:
        if not settings.RATE_LIMIT_ENABLED:
            return True

        limit = custom_limit or self.limit
        now = time.time()
        redis_conn = self._get_redis()

        if redis_conn:
            try:
                redis_key = f"{self.prefix}:{key}"
                pipe = redis_conn.pipeline()
                window_start = now - self.window
                pipe.zremrangebyscore(redis_key, 0, window_start)
                pipe.zadd(redis_key, {f"{now}-{secrets.token_hex(4)}": now})
                pipe.zcard(redis_key)
                pipe.expire(redis_key, self.window + 5)
                _, _, count, _ = pipe.execute()
                return count <= limit
            except Exception as e:
                logger.warning(f"Redis rate check error: {e}. Falling back to in-memory check.")
                self._redis_available = False
                self._last_retry_time = time.time()

        # In-memory sliding window fallback
        window_start = now - self.window
        timestamps = [t for t in self._memory_requests[key] if t > window_start]
        self._memory_requests[key] = timestamps
        if len(timestamps) >= limit:
            return False
        self._memory_requests[key].append(now)
        return True

# Backward compatible alias
SlidingWindowRateLimiter = RateLimiter

auth_rate_limiter = RateLimiter(
    limit=settings.AUTH_RATE_LIMIT_PER_MINUTE,
    window_seconds=60,
    prefix="auth_limit"
)

ai_rate_limiter = RateLimiter(
    limit=settings.AI_RATE_LIMIT_PER_MINUTE,
    window_seconds=60,
    prefix="ai_limit"
)

def check_auth_rate_limit(request: Request):
    """
    FastAPI dependency to rate-limit authentication endpoints by client IP.
    """
    client_ip = request.client.host if request.client else "unknown"
    if not auth_rate_limiter.is_allowed(client_ip, custom_limit=settings.AUTH_RATE_LIMIT_PER_MINUTE):
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Too many authentication attempts. Please slow down and try again in one minute."
        )

def check_ai_rate_limit(request: Request):
    """
    FastAPI dependency to rate-limit expensive AI endpoints by client IP.
    """
    client_ip = request.client.host if request.client else "unknown"
    if not ai_rate_limiter.is_allowed(client_ip, custom_limit=settings.AI_RATE_LIMIT_PER_MINUTE):
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="AI inference rate limit exceeded. Please wait a moment before sending more requests."
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
        "iss": "edupath-ai-auth",
        "jti": secrets.token_hex(16)
    }
    encoded_jwt = jwt.encode(to_encode, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)
    return encoded_jwt

# In-memory token revocation cache (stored by raw token string or jti)
_revoked_tokens: set = set()

def revoke_token(token: str) -> None:
    """
    Revokes an issued JWT access token upon logout to invalidate the session.
    Records both the raw token string and the cryptographic jti claim.
    """
    if not token or not isinstance(token, str):
        return
    token_str = token.strip()
    _revoked_tokens.add(token_str)

    jti = None
    try:
        unverified_payload = jwt.decode(
            token_str,
            settings.JWT_SECRET,
            algorithms=[settings.JWT_ALGORITHM],
            options={"verify_exp": False, "verify_iss": False, "verify_signature": False}
        )
        jti = unverified_payload.get("jti")
        if jti:
            _revoked_tokens.add(str(jti))
    except Exception:
        pass

    # If Redis is active, replicate revocation across distributed cluster
    try:
        redis_conn = auth_rate_limiter._get_redis()
        if redis_conn:
            ttl_seconds = settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
            redis_conn.setex(f"revoked_token:{token_str}", ttl_seconds, "1")
            if jti:
                redis_conn.setex(f"revoked_token:{jti}", ttl_seconds, "1")
    except Exception as e:
        logger.warning(f"Failed to record token revocation in Redis: {e}")

def is_token_revoked(token_or_jti: str) -> bool:
    """
    Checks if a JWT access token or its jti has been explicitly invalidated / revoked.
    """
    if not token_or_jti or not isinstance(token_or_jti, str):
        return False
    val_str = token_or_jti.strip()
    if val_str in _revoked_tokens:
        return True
    try:
        redis_conn = auth_rate_limiter._get_redis()
        if redis_conn:
            return bool(redis_conn.exists(f"revoked_token:{val_str}"))
    except Exception:
        pass
    return False

def decode_access_token(token: str) -> Optional[str]:
    if is_token_revoked(token):
        return None
    try:
        payload = jwt.decode(
            token,
            settings.JWT_SECRET,
            algorithms=[settings.JWT_ALGORITHM],
            options={"verify_exp": True, "verify_iss": True},
            issuer="edupath-ai-auth"
        )
        jti = payload.get("jti")
        if jti and is_token_revoked(str(jti)):
            return None
        user_id = payload.get("sub")
        if not user_id or not str(user_id).strip():
            return None
        return str(user_id).strip()
    except (JWTError, ExpiredSignatureError):
        return None

def is_safe_upload_path(base_dir: str, target_path: str) -> bool:
    """
    Validates that target_path resolves strictly within base_dir using os.path.commonpath().
    Protects against directory traversal (../), sibling-directory prefix matching
    (e.g., /app/uploads_evil vs /app/uploads), and symlink escape attacks.
    """
    if not base_dir or not target_path:
        return False
    try:
        real_base = os.path.realpath(base_dir)
        real_target = os.path.realpath(target_path)
        # Sibling directory check via commonpath:
        # commonpath must resolve strictly to real_base
        if os.path.commonpath([real_base, real_target]) != real_base:
            return False
        # Target path cannot be the upload base directory itself
        if real_base == real_target:
            return False
        return True
    except (ValueError, OSError):
        return False

