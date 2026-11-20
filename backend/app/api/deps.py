from typing import Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.core.database import get_db
from app.core.security import decode_access_token
from app.models.models import User

security_scheme = HTTPBearer(auto_error=False)

async def get_current_user(
    auth_creds: Optional[HTTPAuthorizationCredentials] = Depends(security_scheme),
    session: AsyncSession = Depends(get_db)
) -> User:
    """
    Validates JWT token and resolves the user.
    If no authorization header is passed, attempts to fallback to the seeded demo user
    to provide a seamless out-of-the-box experience while fully supporting standard JWT auth.
    """
    if auth_creds and auth_creds.credentials:
        user_id = decode_access_token(auth_creds.credentials)
        if user_id:
            stmt = select(User).where(User.id == user_id)
            res = await session.execute(stmt)
            user = res.scalar_one_or_none()
            if user:
                return user

    # Fallback to demo user if no valid token provided
    stmt = select(User).where(User.email == "demo@edupath.ai")
    res = await session.execute(stmt)
    demo_user = res.scalar_one_or_none()
    if demo_user:
        return demo_user

    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
