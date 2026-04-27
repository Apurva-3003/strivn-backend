"""JWT creation and FastAPI dependency for the current authenticated user."""

from __future__ import annotations

import os
from datetime import datetime, timedelta, timezone
from uuid import UUID

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError, jwt
from sqlalchemy.orm import Session

from app.database.db import get_db
from app.database.models import User

ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 10080

oauth2_scheme = HTTPBearer()


def get_secret_key() -> str:
    """Return JWT signing secret from the environment, or raise if unset."""
    key = os.getenv("SECRET_KEY")
    if not key or not key.strip():
        raise RuntimeError(
            "SECRET_KEY environment variable must be set to a non-empty string for JWT authentication."
        )
    return key


def require_secret_key_at_startup() -> None:
    """Validate SECRET_KEY is configured; call from application lifespan."""
    get_secret_key()


def create_access_token(data: dict) -> str:
    """Sign a JWT (HS256) with 30-minute expiry. Raises if SECRET_KEY is missing."""
    secret = get_secret_key()
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode["exp"] = expire
    return jwt.encode(to_encode, secret, algorithm=ALGORITHM)


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    token = credentials.credentials
    try:
        secret = get_secret_key()
        payload = jwt.decode(token, secret, algorithms=[ALGORITHM])
        sub = payload.get("sub")
        if sub is None:
            raise credentials_exception
        user_id = UUID(str(sub))
    except (JWTError, ValueError):
        raise credentials_exception from None
    user = db.get(User, user_id)
    if user is None:
        raise credentials_exception
    return user
