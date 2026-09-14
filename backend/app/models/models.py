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
    sessions = relationship("StudySession", back_populates= "user", cascade = "all.delete")