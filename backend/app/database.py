from sqlalchemy import create_engine 
#SQLALCHEMY is a library for communicating with relational db, ex.MYSQL, PostgreSQL, SQLITE,Oracle, Microsoft SQL SERver

from sqlalchemy.ext.declarative import declarative_base

from sqlalchemy.orm import sessionmaker
# session_maker used to perform opertaions such as insert, select, update, delete, commit, rollback.Each API request  can get its own database session.
from app.config import get_settings

settings = get_settings()
# Creates a database engine, manager of db
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
