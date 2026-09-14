from sqlalchemy import Column , String, Integer, DateTime,  Text, ForeignKey, Boolean

from sqlachemy.orm import relationship

from sqlalchemy.sql import func
import uuid
from app.database import Base

class User(Base):
    __tablename__ = "users"
    id =Column(String, primary_key=True, default = gen__uuid)
    email = Column(String, unique=True, index = True, nullable=False)
    hashed_password = Column(String, nullable = False)
    is_active = Column(Boolean, default = True)
    created_at = Column(DateTime(timezone =True),  server_default = func.now())
    sessions = relationship("StudySession", back_populates= "user", cascade = "all, delete")

class StudySession(Base):
   
    __tablename__ = "study_sessions"
   
    id = Column(String, primary_key=True, default = gen_uuid)
   
    user_id= Column(String, ForeignKey("user.id",ondelete="CASCADE"), nullable=True)
   
    label = Column(String, nullable=True)
   
    is_guest= Column(Boolean, default=False)
   
    status = Column(String, default = "active")
   
    created_at = Column(DateTime(timezone=True), sever_default= func.now())

    user = relationship("User", back_populates="sessions")
    
    files = relationship("UploadFile", back_populates="session", cascade="all delete")
    
    messages = relationship("Message", back_populates ="session",cascade="all delete")

class UploadFile(Base):
    __tablename__ = "upload_files"

    id = Column(String, primary_key = True, default = gen_uuid)

    session_id = Column(String, Foreign_key("study_session.id",ondelete = "CASCADE"), nullable= False)

    original_name = Column(String, nullable=False)

    stored_name = Column(String, nullable=False)

    file_type = Column(String, nullable=False)

    file_size = Column(Integer, nullable=False)

    status = Column(String, default="processing")

    chunk_count = Column(Integer, default = 0)

    created_at = Column(DateTime(timezone=True), server_default=func.now())

    session = relationship("StudySession", back_populates="files")

class Message(Base):
    __tablename__ = "messages"
    id = Column(String, primary_key = True, default = gen_uuid)

    session_id = Column(String, ForeignKey("study_sessions.id", ondelete="CASCADE"), nullable= False)

    role = Column(String, nullable = False)

    content = Column(Text, nullable =False)

    created_at = Column(DateTime(timezone=True), server_default=func.now())

    session = relationship("StudySession", back_populates="messages")

