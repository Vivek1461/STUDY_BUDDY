"""FastAPI application composition and operational endpoints."""
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import get_settings
from app.routers import auth, chat, upload, sessions

settings = get_settings()
logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s %(message)s")

@asynccontextmanager
async def lifespan(_: FastAPI):
    settings.upload_dir.mkdir(parents=True, exist_ok=True)
    settings.chroma_persist_dir.mkdir(parents=True, exist_ok=True)
    yield

app = FastAPI(title="Study Buddy API", version="1.0.0", lifespan=lifespan)
app.add_middleware(CORSMiddleware, allow_origins=settings.cors_origins,
                   allow_credentials=True, allow_methods=["GET", "POST", "DELETE"],
                   allow_headers=["Authorization", "Content-Type"])
app.include_router(auth.router, prefix="/api")
app.include_router(sessions.router, prefix="/api")
app.include_router(upload.router, prefix="/api")
app.include_router(chat.router, prefix="/api")

@app.get("/health/live", tags=["operations"])
def liveness():
    return {"status": "ok"}

@app.get("/health/ready", tags=["operations"])
def readiness():
    # Process readiness only; external dependencies are checked by dedicated monitoring.
    return {"status": "ready"}
