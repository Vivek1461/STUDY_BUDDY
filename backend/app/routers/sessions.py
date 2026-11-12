"""Study-session listing and ownership-safe session operations."""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import StudySession
from app.schemas.schemas import SessionOut
from app.services.auth import RequestIdentity, require_identity

router = APIRouter(prefix="/sessions", tags=["sessions"])

def get_owned_session(session_id: str, identity: RequestIdentity, db: Session) -> StudySession:
    session = db.query(StudySession).filter(
        StudySession.id == session_id, StudySession.status == "active"
    ).first()
    if session is None:
        raise HTTPException(status_code=404, detail="Session not found")
    if identity.kind == "user" and session.user_id != identity.subject:
        raise HTTPException(status_code=404, detail="Session not found")
    if identity.kind == "guest" and (not session.is_guest or identity.session_id != session.id):
        raise HTTPException(status_code=404, detail="Session not found")
    return session

@router.get("", response_model=list[SessionOut])
def list_sessions(db: Session = Depends(get_db),
                  identity: RequestIdentity = Depends(require_identity)):
    if identity.kind == "guest":
        query = db.query(StudySession).filter(StudySession.id == identity.session_id,
                                              StudySession.is_guest.is_(True))
    else:
        query = db.query(StudySession).filter(StudySession.user_id == identity.subject,
                                              StudySession.is_guest.is_(False))
    return query.order_by(StudySession.created_at.desc()).all()

@router.get("/{session_id}", response_model=SessionOut)
def read_session(session_id: str, db: Session = Depends(get_db),
                 identity: RequestIdentity = Depends(require_identity)):
    return get_owned_session(session_id, identity, db)
