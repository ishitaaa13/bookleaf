
import os
from datetime import datetime, timedelta, timezone

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from pwdlib import PasswordHash
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.config import APP_ENV
from app.database import get_db
from app.models import UserAccount

JWT_SECRET = os.getenv("JWT_SECRET")

if not JWT_SECRET:
    if APP_ENV.lower() == "development":
        JWT_SECRET = "local-development-secret-change-before-deployment"
    else:
        raise RuntimeError("JWT_SECRET must be set outside development.")

JWT_ALGORITHM = "HS256"
ACCESS_TOKEN_MINUTES = 30

password_hash = PasswordHash.recommended()
bearer_scheme = HTTPBearer()


def hash_password(password: str) -> str:
    return password_hash.hash(password)


def verify_password(password: str, hashed_password: str) -> bool:
    return password_hash.verify(password, hashed_password)


def create_access_token(user: UserAccount) -> str:
    now = datetime.now(timezone.utc)

    payload = {
        "sub": str(user.user_id),
        "role": user.role,
        "iat": now,
        "exp": now + timedelta(minutes=ACCESS_TOKEN_MINUTES),
    }

    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
    db: Session = Depends(get_db),
) -> UserAccount:
    unauthorized = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid or expired authentication token.",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = jwt.decode(
            credentials.credentials,
            JWT_SECRET,
            algorithms=[JWT_ALGORITHM],
        )
        user_id = int(payload["sub"])
    except (jwt.InvalidTokenError, KeyError, TypeError, ValueError):
        raise unauthorized

    user = db.scalar(
        select(UserAccount).where(UserAccount.user_id == user_id)
    )

    if user is None or not user.is_active:
        raise unauthorized

    return user


def require_role(required_role: str):
    def role_checker(
        current_user: UserAccount = Depends(get_current_user),
    ) -> UserAccount:
        if current_user.role != required_role:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You do not have permission to access this resource.",
            )
        return current_user

    return role_checker
