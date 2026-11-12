"""Authentication, token verification and request identity."""
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from typing import Optional
import bcrypt
from jose import JWTError, jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from app.config import get_settings
from app.database import get_db
from app.models import User

settings = get_settings()
_bearer = HTTPBearer(auto_error=False)

@dataclass(frozen=True)
class RequestIdentity:
    subject: str
    kind: str
    session_id: str | None = None
    user: User | None = None

def hash_password(password: str) -> str:
    raw = password.encode("utf-8")
    if len(raw) > 72:
        raise ValueError("Password must be at most 72 UTF-8 bytes")
    return bcrypt.hashpw(raw, bcrypt.gensalt(rounds=12)).decode("utf-8")

def verify_password(plain: str, hashed: str) -> bool:
    try:
        raw = plain.encode("utf-8")
        return len(raw) <= 72 and bcrypt.checkpw(raw, hashed.encode("utf-8"))
    except (ValueError, TypeError):
        return False

def create_access_token(subject: str, kind: str = "user", session_id: str | None = None) -> str:
    now = datetime.now(timezone.utc)
    claims = {"sub": subject, "typ": kind, "iat": now,
              "exp": now + timedelta(minutes=settings.access_token_expire_minutes)}
    if session_id:
        claims["sid"] = session_id
    return jwt.encode(claims, settings.secret_key.get_secret_value(), algorithm=settings.algorithm)

def get_identity(credentials: Optional[HTTPAuthorizationCredentials] = Depends(_bearer),
                 db: Session = Depends(get_db)) -> RequestIdentity | None:
    if credentials is None:
        return None
    try:
        claims = jwt.decode(credentials.credentials, settings.secret_key.get_secret_value(),
                             algorithms=[settings.algorithm])
        subject, kind = claims.get("sub"), claims.get("typ")
        if not subject or kind not in {"user", "guest"}:
            raise JWTError("Invalid token claims")
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid or expired access token",
                            headers={"WWW-Authenticate": "Bearer"})
    if kind == "guest":
        return RequestIdentity(subject=subject, kind="guest", session_id=claims.get("sid"))
    user = db.query(User).filter(User.id == subject, User.is_active.is_(True)).first()
    if user is None:
        raise HTTPException(status_code=401, detail="User account is unavailable")
    return RequestIdentity(subject=subject, kind="user", user=user)

def get_current_user(identity: RequestIdentity | None = Depends(get_identity)) -> User | None:
    return identity.user if identity and identity.kind == "user" else None

def require_user(identity: RequestIdentity | None = Depends(get_identity)) -> User:
    if identity is None or identity.kind != "user" or identity.user is None:
        raise HTTPException(status_code=401, detail="Authentication required",
                            headers={"WWW-Authenticate": "Bearer"})
    return identity.user

def require_identity(identity: RequestIdentity | None = Depends(get_identity)) -> RequestIdentity:
    if identity is None:
        raise HTTPException(status_code=401, detail="Authentication required",
                            headers={"WWW-Authenticate": "Bearer"})
    return identity
