from sqlalchemy import create_engine 
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from app.config import get_settings

settings = get_settings()

engine = create_engine(settings.database_url)
SessionLocal = sessionmaker(autocommit = False, autoflush= False, bind=engine)
Base = declerative_base()

def get_db():
    db= SessionLocal()
    try:
        yield db 
        #yield in get_db() -> FastAPI automatically closes the DB connection after each request Finishes.
    finally:
        db.close()
