"""Relational persistence models."""
import uuid
from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Index, Integer, String, Text, func
from sqlalchemy.orm import relationship
from app.database import Base

def new_id() -> str:
    return str(uuid.uuid4())

class User(Base):
    __tablename__ = "users"
    id = Column(String(36), primary_key=True, default=new_id)
    email = Column(String(320), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    is_active = Column(Boolean, nullable=False, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    sessions = relationship("StudySession", back_populates="user", cascade="all, delete-orphan")

class StudySession(Base):
    __tablename__ = "study_sessions"
    id = Column(String(36), primary_key=True, default=new_id)
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=True, index=True)
    label = Column(String(255))
    is_guest = Column(Boolean, nullable=False, default=False)
    status = Column(String(20), nullable=False, default="active")
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    user = relationship("User", back_populates="sessions")
    files = relationship("UploadFile", back_populates="session", cascade="all, delete-orphan")
    messages = relationship("Message", back_populates="session", cascade="all, delete-orphan")

class UploadFile(Base):
    __tablename__ = "upload_files"
    id = Column(String(36), primary_key=True, default=new_id)
    session_id = Column(String(36), ForeignKey("study_sessions.id", ondelete="CASCADE"), nullable=False, index=True)
    original_name = Column(String(255), nullable=False)
    stored_name = Column(String(255), unique=True, index=True, nullable=False)
    file_type = Column(String(20), nullable=False)
    file_size = Column(Integer, nullable=False)
    status = Column(String(20), nullable=False, default="processing")
    chunk_count = Column(Integer, nullable=False, default=0)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    session = relationship("StudySession", back_populates="files")

class Message(Base):
    __tablename__ = "messages"
    id = Column(String(36), primary_key=True, default=new_id)
    session_id = Column(String(36), ForeignKey("study_sessions.id", ondelete="CASCADE"), nullable=False, index=True)
    role = Column(String(20), nullable=False)
    content = Column(Text, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    session = relationship("StudySession", back_populates="messages")

Index("ix_messages_session_created", Message.session_id, Message.created_at)
