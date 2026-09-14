from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from app.config import get_settings
from app.database import get_db
from app.models import User

settings = get_settings()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated='auto')
bearer_scheme= HTTPBearer(auto_error=False)

def hash_password(password: str)-> str:
    return pwd_context.hash(password)

def verify_password(plain:str , hashed: str)->bool :
    return pwd_context.verify(plain, hashed)

def create_access_token(data:dict, expires_delta: Optional[timedelta]=None)-> str:
    to_encode = data.copy()
    expire = datetime.utcnow()+ (expires_delta or timedelta(minutes = settings.access_token_expire_minutes))
    to_encode["exp"]= expire
    return jwt.encode(to_encode, settings.secret_key, algorithm=settings.algorithm)

def get_current_user(
    credentials:Optional[HTTPAuthorizationCredentials]=Depends(bearer_scheme), db: Session =Depends(get_db)) -> Optional[User]:
    if credentials is None:
        return None
    try:
        payload = jwt.decode(credentials.credentials, settings.secret_key, algorithms=[settings.algorithm])
        user_id: str = payload.get("sub")
        if user_id is None:
            return None
    except JWTError:
        return None
    return db.query(User).filter(User.id == user_id).first()

def reuire_user(current_user: Optional[User]= Depends(get_current_user))-> User:
    if current_user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail = "Authentication required")
    return current_user


