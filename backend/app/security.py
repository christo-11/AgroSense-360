from datetime import datetime, timedelta, timezone
from uuid import UUID

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jwt import InvalidTokenError
from pwdlib import PasswordHash
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.config import get_settings
from app.database import get_db
from app.models import User

password_hash = PasswordHash.recommended()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/token")


def hash_password(password: str) -> str:
    return password_hash.hash(password)


def verify_password(password: str, stored_hash: str) -> bool:
    return password_hash.verify(password, stored_hash)


def create_access_token(user_id: UUID) -> str:
    settings = get_settings()
    if not settings.auth_configured:
        raise HTTPException(status_code=503, detail="Authentication is not configured with a secure JWT secret.")
    expires = datetime.now(timezone.utc) + timedelta(minutes=30)
    return jwt.encode({"sub": str(user_id), "exp": expires}, settings.jwt_secret_value, algorithm="HS256")


def current_user(
    token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)
) -> User:
    return _load_user(token, db, allow_password_change=False)


def password_change_user(
    token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)
) -> User:
    return _load_user(token, db, allow_password_change=True)


def _load_user(token: str, db: Session, *, allow_password_change: bool) -> User:
    settings = get_settings()
    if settings.public_demo_mode:
        raise HTTPException(status_code=503, detail="Authentication is disabled in public demo mode.")
    if not settings.auth_configured:
        raise HTTPException(status_code=503, detail="Authentication is not configured with a secure JWT secret.")
    credentials_error = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid or expired authentication credentials.",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, settings.jwt_secret_value, algorithms=["HS256"])
        subject = payload.get("sub")
        user_id = UUID(subject) if isinstance(subject, str) else None
    except (InvalidTokenError, ValueError):
        raise credentials_error from None
    if user_id is None:
        raise credentials_error
    user = db.scalar(select(User).where(User.id == user_id))
    if user is None:
        raise credentials_error
    if user.must_change_password and not allow_password_change:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Change your temporary password before using AgroSense.",
        )
    return user


def agricultural_admin(user: User = Depends(current_user)) -> User:
    if user.email.casefold() not in get_settings().agricultural_admin_email_set:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Administrative access is required.")
    return user
