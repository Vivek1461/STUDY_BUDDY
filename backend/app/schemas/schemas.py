from pydantic import BaseModel, EmailStr
from typing import Optional, List 
from datetime import datetime
# ── Auth ─────────

class UserCreate(BaseModel):
    email: EmailStr
    password: str

class UserOut(BaseModel):
    id:str
    email:str
    created_at: datetime
    
    class Config:
        from attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str ="bearer"

class GuestSession(BaseModel):
    session_id: str
    message: str ="Gest session created"

#Sessions-----------------------------
class FileOut(BaseModel):
    id: str
    original_name: str
    file_type: str
    file_size: int 
    status: str
    chunk_count: int
    created_at: datetime
    class Config:
        from_attributes = True

class SessionOut(BaseModel):
    id : str
    label: Optional[str]
    is_guest: bool
    status: str
    created_at: datetime
    files: List[FileOut]=[]

    class Config:
        from_attributes = True

#------Chat_-------------------------
class ChatMessage(BaseModel):
    message: str
    action: Optional[str]= None # teach | keypoints | quiz | examtips

class MessageOut(BaseModel):
    id: str
    role: str
    content: str
    created_at: datetime
    class Config:
        from_attributes= True
# ── Upload ────────────────────────────────────────────────────
class UploadResponse(BaseModel):
    session_id: str
    file: FileOut
    message: str
    


