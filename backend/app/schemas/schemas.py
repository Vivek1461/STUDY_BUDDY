"""Validated request and response contracts."""
from datetime import datetime
from typing import Literal
from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator

class UserCreate(BaseModel):
    email: EmailStr
    password: str = Field(min_length=10, max_length=72)

class LoginRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=1, max_length=72)

class UserOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str
    email: EmailStr
    created_at: datetime

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"

class GuestSession(BaseModel):
    session_id: str
    access_token: str
    token_type: str = "bearer"
    message: str = "Guest session created"

class FileOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str
    original_name: str
    file_type: str
    file_size: int
    status: str
    chunk_count: int
    created_at: datetime

class SessionOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str
    label: str | None
    is_guest: bool
    status: str
    created_at: datetime
    files: list[FileOut] = Field(default_factory=list)

class ChatMessage(BaseModel):
    message: str = Field(min_length=1, max_length=8000)
    action: Literal["teach", "keypoints", "quiz", "examtips"] | None = None

class MessageOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str
    role: str
    content: str
    created_at: datetime

class UploadResponse(BaseModel):
    session_id: str
    file: FileOut
    message: str
