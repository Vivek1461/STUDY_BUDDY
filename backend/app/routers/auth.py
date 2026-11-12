"""Registration, login and anonymous study-session endpoints."""
import uuid
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import StudySession, User
from app.schemas.schemas import UserCreate, UserOut, LoginRequest, Token, GuestSession
from app.services.auth import hash_password, verify_password, create_access_token

router = APIRouter(prefix="/auth", tags=["authentication"])

@router.post("/register", response_model=UserOut, status_code=status.HTTP_201_CREATED)
def register(payload: UserCreate, db: Session = Depends(get_db)):
    email = str(payload.email).strip().lower()
    if db.query(User).filter(User.email == email).first():
        raise HTTPException(status_code=409, detail="An account with this email already exists")
    user = User(email=email, hashed_password=hash_password(payload.password))
    db.add(user)
    try:
        db.commit()
        db.refresh(user)
    except Exception:
        db.rollback()
        raise HTTPException(status_code=409, detail="Unable to create account with these details")
    return user

@router.post("/login", response_model=Token)
def login(payload: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == str(payload.email).lower()).first()
    if not user or not user.is_active or not verify_password(payload.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Incorrect email or password",
                            headers={"WWW-Authenticate": "Bearer"})
    return Token(access_token=create_access_token(user.id))

@router.post("/guest", response_model=GuestSession, status_code=201)
def create_guest_session(db: Session = Depends(get_db)):
    session_id = str(uuid.uuid4())
    session = StudySession(id=session_id, is_guest=True, label="Guest study session")
    db.add(session)
    db.commit()
    return GuestSession(session_id=session_id,
                        access_token=create_access_token(f"guest:{session_id}", kind="guest", session_id=session_id))
