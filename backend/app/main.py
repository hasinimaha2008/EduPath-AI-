import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.core.init_db import init_database

# Import API Routers
from app.api.auth import router as auth_router
from app.api.documents import router as documents_router
from app.api.assistant import router as assistant_router
from app.api.notes import router as notes_router
from app.api.quizzes import router as quizzes_router
from app.api.analytics import router as analytics_router
from app.api.topic_performance import router as topics_router
from app.api.careers import router as careers_router
from app.api.skill_mapping import router as skill_mapping_router
from app.api.skill_gaps import router as skill_gaps_router
from app.api.roadmaps import router as roadmaps_router
from app.api.study_planner import router as study_planner_router
from app.api.chat_history import router as chat_history_router
from app.api.subjects import router as subjects_router
from app.api.voice import router as voice_router
from app.api.insights import router as insights_router
from app.api.workspace import router as workspace_router
from app.api.notifications import router as notifications_router
from app.api.profile import router as profile_router

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger("edupath")

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Initializing EduPath AI services & taxonomy database...")
    try:
        await init_database()
        logger.info("EduPath AI Database & Taxonomy ready.")
    except Exception as e:
        logger.error(f"Error initializing database: {e}")
    yield
    logger.info("Shutting down EduPath AI services...")

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="Intelligent Learning & Career Ecosystem – Learn Smarter. Grow Better. Build Your Career.",
    lifespan=lifespan
)

# Centralized Environment-Based CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type", "Accept", "Origin", "X-Requested-With"],
)

# Exception handler for unhandled errors
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled error at {request.url.path}: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "An internal server error occurred. Please try again or check system logs."}
    )

# Include All Routers
app.include_router(auth_router, prefix=settings.API_V1_PREFIX)
app.include_router(documents_router, prefix=settings.API_V1_PREFIX)
app.include_router(assistant_router, prefix=settings.API_V1_PREFIX)
app.include_router(notes_router, prefix=settings.API_V1_PREFIX)
app.include_router(quizzes_router, prefix=settings.API_V1_PREFIX)
app.include_router(analytics_router, prefix=settings.API_V1_PREFIX)
app.include_router(topics_router, prefix=settings.API_V1_PREFIX)
app.include_router(careers_router, prefix=settings.API_V1_PREFIX)
app.include_router(skill_mapping_router, prefix=settings.API_V1_PREFIX)
app.include_router(skill_gaps_router, prefix=settings.API_V1_PREFIX)
app.include_router(roadmaps_router, prefix=settings.API_V1_PREFIX)
app.include_router(study_planner_router, prefix=settings.API_V1_PREFIX)
app.include_router(chat_history_router, prefix=settings.API_V1_PREFIX)
app.include_router(subjects_router, prefix=settings.API_V1_PREFIX)
app.include_router(voice_router, prefix=settings.API_V1_PREFIX)
app.include_router(insights_router, prefix=settings.API_V1_PREFIX)
app.include_router(workspace_router, prefix=settings.API_V1_PREFIX)
app.include_router(notifications_router, prefix=settings.API_V1_PREFIX)
app.include_router(profile_router, prefix=settings.API_V1_PREFIX)

@app.get("/")
async def root():
    return {
        "platform": "EduPath AI – Intelligent Learning & Career Ecosystem",
        "tagline": "Learn Smarter. Grow Better. Build Your Career.",
        "status": "operational",
        "version": settings.VERSION,
        "docs_url": "/docs"
    }

from sqlalchemy import text
from app.core.database import AsyncSessionLocal
import os

@app.get("/health")
@app.get("/api/health")
async def health_check():
    """
    Production health check probing database connectivity and upload storage write permissions.
    """
    db_status = "connected"
    try:
        async with AsyncSessionLocal() as session:
            await session.execute(text("SELECT 1"))
    except Exception as e:
        logger.error(f"Health check probe failed on database connection: {e}")
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content={
                "status": "unhealthy",
                "service": "EduPath AI Backend Engine",
                "database": f"error: {str(e)}",
                "version": settings.VERSION
            }
        )

    storage_writable = os.access(settings.UPLOAD_DIR, os.W_OK) if os.path.exists(settings.UPLOAD_DIR) else True
    return {
        "status": "healthy",
        "service": "EduPath AI Backend Engine",
        "database": db_status,
        "storage": "writable" if storage_writable else "read-only",
        "environment": settings.ENVIRONMENT,
        "version": settings.VERSION
    }
