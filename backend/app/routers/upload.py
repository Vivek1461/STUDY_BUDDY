"""Document upload and deletion endpoints with session authorization."""
import logging, uuid
from pathlib import Path
from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile as IncomingFile, status
from fastapi.concurrency import run_in_threadpool
from sqlalchemy.orm import Session
from app.config import get_settings
from app.database import get_db
from app.models import StudySession, UploadFile
from app.schemas.schemas import UploadResponse, FileOut
from app.services.auth import RequestIdentity, require_identity
from app.routers.sessions import get_owned_session
from app.services.parser import detect_file_type, extract_text
from app.services.rag import index_document, delete_file_index

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/upload", tags=["documents"])
settings = get_settings()
ALLOWED_EXTENSIONS = {".pdf", ".docx", ".pptx", ".jpg", ".jpeg", ".png", ".txt"}

@router.post("", response_model=UploadResponse, status_code=status.HTTP_201_CREATED)
async def upload_file(file: IncomingFile = File(...), session_id: str | None = Form(None),
                      label: str | None = Form(None), db: Session = Depends(get_db),
                      identity: RequestIdentity = Depends(require_identity)):
    filename = Path(file.filename or "").name
    extension = Path(filename).suffix.lower()
    if not filename or extension not in ALLOWED_EXTENSIONS:
        raise HTTPException(status_code=400, detail="Unsupported file type")
    max_bytes = settings.max_upload_size_mb * 1024 * 1024
    content = await file.read(max_bytes + 1)
    if not content:
        raise HTTPException(status_code=400, detail="The uploaded file is empty")
    if len(content) > max_bytes:
        raise HTTPException(status_code=413, detail=f"File exceeds the {settings.max_upload_size_mb} MB limit")
    file_type = detect_file_type(filename)
    target_session = session_id or (identity.session_id if identity.kind == "guest" else None)
    if target_session:
        session = get_owned_session(target_session, identity, db)
    else:
        session = StudySession(user_id=identity.subject, is_guest=False, label=(label or filename)[:255])
        db.add(session)
        db.commit()
        db.refresh(session)
    stored_name = f"{uuid.uuid4().hex}{extension}"
    settings.upload_dir.mkdir(parents=True, exist_ok=True)
    destination = settings.upload_dir / stored_name
    record = UploadFile(session_id=session.id, original_name=filename[:255], stored_name=stored_name,
                        file_type=file_type, file_size=len(content), status="processing")
    indexed = False
    try:
        destination.write_bytes(content)
        db.add(record)
        db.commit()
        db.refresh(record)
        extracted = await run_in_threadpool(extract_text, str(destination), file_type)
        if not extracted.strip():
            raise ValueError("No readable text was found in this document")
        chunks = await run_in_threadpool(index_document, session.id, record.id, filename, extracted)
        if chunks < 1:
            raise ValueError("No indexable text was found")
        indexed = True
        record.status, record.chunk_count = "ready", chunks
        db.commit()
        db.refresh(record)
    except Exception as exc:
        db.rollback()
        if indexed:
            try:
                await run_in_threadpool(delete_file_index, session.id, record.id)
            except Exception:
                logger.exception("Failed to roll back vector index")
        try:
            persisted = db.query(UploadFile).filter(UploadFile.id == record.id).first()
            if persisted:
                db.delete(persisted)
                db.commit()
        except Exception:
            db.rollback()
            logger.exception("Failed to roll back upload metadata")
        destination.unlink(missing_ok=True)
        logger.exception("Document processing failed")
        raise HTTPException(status_code=422, detail="The document could not be processed") from exc
    return UploadResponse(session_id=session.id, file=FileOut.model_validate(record),
                          message=f"Uploaded and indexed ({chunks} chunks)")

@router.delete("/{file_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_file(file_id: str, db: Session = Depends(get_db),
                identity: RequestIdentity = Depends(require_identity)):
    record = db.query(UploadFile).filter(UploadFile.id == file_id).first()
    if record is None:
        raise HTTPException(status_code=404, detail="File not found")
    session = get_owned_session(record.session_id, identity, db)
    try:
        delete_file_index(session.id, record.id)
    except Exception:
        logger.exception("Vector cleanup failed for file %s", record.id)
        raise HTTPException(status_code=503, detail="Document cleanup is temporarily unavailable")
    path = settings.upload_dir / record.stored_name
    db.delete(record)
    db.commit()
    path.unlink(missing_ok=True)
    return None
