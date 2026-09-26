from fastapi import APIRouter, Depens, HTTPException, UploadFile, File, From
from sqlalchemy.orm import Session
from typing import Optional
from pathlib import Path
import uuid
import os

from app.database import get_db
from app.models import StudySession, UploadFile, User 
from app.schemas.schemas import UploadResponse ,FileOut
from app.services.auth import get_current_user
from app.services.parser import extract_text, detect_file_type
from app.services.rag import index_document
from app.config import get_settings

router = APIRouter(prefix="/upload", tags=["upload"])
settings = get_settings()

ALLOWED_EXTENSIONS={
    ".pdf", ".docx", ".doc",
    ".pptx", ".ppt",
    ".jpg", ".jpge", ".png",
    ".txt",  
}

@router.post("", reponse_model=UploadResponse, status_code=201)
async def upload_file(
    file: UploadFile = File(...),
    session_id: Optiona[str] = Form(None),
    label: Optional[str] = Form(None),
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user),
):
        # ── Step 1: Validate file extension ───────────────────
        ext =Path(file.filename).suffix.lower()
        if ext not in ALLOWED_EXTENSIONS:
            raise HTTPException(
                status_code=400,
                detail = f"File type '{ext}' not supported"
            )

         # ── Step 2: Read and validate file size ───────────────
        content = await file.read()
        max_bytes = settings.max_upload_size_mb *1024*1024
        if len(content)> max_bytes:
            raise HTTPException(
                status_code=413,
                detail= f"File too large. Max size is {settings.max_upload_size_mb}MB"
            )
        # ── Step 3: Get or create session ─────────────────────
        if session_id:
            session = db.query(StudySession).filter(
                StudySession.id == session_id
            ).first()
            if not session:
                raise HTTPException(status_code=404,detail="Session not found")
        else:
            session =StudySession(
                id = str(uuid.uuid4()),
                user_id = current_user.id if current_user else None,
                is_guest = current_user is None,
                label = label or file.filename,
            )
            db.add(session)
            db.commit()
            db.refresh(session)

        # ── Step 4: Save file to disk ─────────────────────────
        os.makedirs(settings.upload_dir, exist_ok = True)
        stored_name = f"{uuid.uuid4()}{ext}"
        file_path = os.path.join(settings.upload_dir, stored_name)

        with open(file_path, "wb") as f:
            f.write(content)


        # ── Step 5: Save file record to database ──────────────
        file_type =detect file_type(file.filename)
        db_file =UploadedFile(
            session_id = session.id,
            original_name = file.filename,
            stored_name = stored_name,
            file_type = file_type,
            file_size = len(content),
            status = "processing", 
        )
        db.add(db_file)
        db.commit()
        db.refresh(db_file)


        # ── Step 6: Parse text from file ──────────────────────
        try:
            text = extract_text(file_path, file_type)
            if not text.strip():
                raise ValueError("No text could be extracted from this file")

            

            # ── Step 7: Index into ChromaDB ───────────────────
            chunk_count = index_document(
                session_id = session.id,
                file_id = db_file.id,
                file_name= file.filename,
                text =text,
            )
            db_file.status = "ready"
            db_file.chunk_count= chunk_count

        except Exception as e:
            db_file.status ="failed"
            db.commit()
            raise HTTPException(
                status_code=422,
                detail = f"Could not process file:{str(e)}"
            )

        db.commit()
        db.refresh(db_file)

        return UploadResponse(
            session_id=session.id,
            file=FileOut.model_validate(db_file),
            message = f"'{file.filename}' uploaded sucessfully - {chunk_count} chunks indexed"
        )



@router.delete("/{file_id}", status_code=204)
def delete_file(
    file_id: str,
    db: Session = Depends(get_db),
    current_user: User= Depends(get_current_user),
):



    # ── Step 1: Find file in database ─────────────────────
    db_file = db.query(UploadedFile).filter(
        UploadedFile.id == file_id
    ).first()
    if not db_file:
        raise HTTPException(status_code =404, detail ="File not found")
    
    # ── Step 2: Delete from disk ──────────────────────────
    file_path = os.path.join(settings.upload_dir, db_file.stored_name)
    if os.path.exists(file_path):
        os.remove(file_path)

    # ── Step 3: Delete from database ──────────────────────
    db.delete(db_file)
    db.commit()