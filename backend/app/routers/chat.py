"""Retrieval-grounded streaming chat endpoint."""
import json
import logging
from fastapi import APIRouter, Depends, HTTPException
from fastapi.concurrency import run_in_threadpool
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Message
from app.schemas.schemas import ChatMessage, MessageOut
from app.services.auth import RequestIdentity, require_identity
from app.routers.sessions import get_owned_session
from app.services.rag import retrieve_context
from app.services.llm import stream_response

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/chat", tags=["chat"])

@router.get("/{session_id}/messages", response_model=list[MessageOut])
def list_messages(session_id: str, db: Session = Depends(get_db),
                  identity: RequestIdentity = Depends(require_identity)):
    session = get_owned_session(session_id, identity, db)
    return db.query(Message).filter(Message.session_id == session.id) \
        .order_by(Message.created_at.asc()).limit(100).all()

@router.post("/{session_id}/messages")
async def send_message(session_id: str, payload: ChatMessage, db: Session = Depends(get_db),
                       identity: RequestIdentity = Depends(require_identity)):
    session = get_owned_session(session_id, identity, db)
    if not session.files:
        raise HTTPException(status_code=409, detail="Upload study material before asking a question")
    history = [{"role": item.role, "content": item.content}
               for item in db.query(Message).filter(Message.session_id == session.id)
               .order_by(Message.created_at.desc()).limit(8).all()][::-1]
    user_record = Message(session_id=session.id, role="user", content=payload.message)
    db.add(user_record)
    db.commit()
    chunks = await run_in_threadpool(retrieve_context, session.id, payload.message, 5)

    def event_stream():
        answer_parts = []
        try:
            for token in stream_response(payload.message, chunks, history, payload.action):
                answer_parts.append(token)
                yield "data: " + json.dumps({"token": token}, ensure_ascii=False) + "\n\n"
            answer = "".join(answer_parts).strip()
            if answer:
                db.add(Message(session_id=session.id, role="assistant", content=answer))
                db.commit()
            yield "data: " + json.dumps({"done": True}) + "\n\n"
        except Exception:
            db.rollback()
            logger.exception("Chat generation failed for session %s", session.id)
            yield "data: " + json.dumps({"error": "AI service temporarily unavailable"}) + "\n\n"

    return StreamingResponse(event_stream(), media_type="text/event-stream",
                             headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"})
