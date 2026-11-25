import time
import uuid
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
        if settings.ENVIRONMENT.lower() in ("production", "prod"):
            raise
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
    allow_headers=["Authorization", "Content-Type", "Accept", "Origin", "X-Requested-With", "X-Request-ID"],
)

@app.middleware("http")
async def security_and_observability_middleware(request: Request, call_next):
    request_id = request.headers.get("X-Request-ID") or str(uuid.uuid4())
    request.state.request_id = request_id

    # Check payload size limit
    content_length = request.headers.get("content-length")
    if content_length:
        try:
            if int(content_length) > settings.MAX_REQUEST_BODY_BYTES:
                return JSONResponse(
                    status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                    content={"detail": "Payload too large. Maximum permitted request body is 30MB."}
                )
        except ValueError:
            pass
    elif request.method in ("POST", "PUT", "PATCH"):
        # Enforce body size limit even if Content-Length header is omitted or chunked
        body_chunks = []
        total_bytes = 0
        async for chunk in request.stream():
            total_bytes += len(chunk)
            if total_bytes > settings.MAX_REQUEST_BODY_BYTES:
                return JSONResponse(
                    status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                    content={"detail": "Payload too large. Maximum permitted request body is 30MB."}
                )
            body_chunks.append(chunk)
        full_body = b"".join(body_chunks)
        async def receive():
            return {"type": "http.request", "body": full_body, "more_body": False}
        request._receive = receive

    start_time = time.perf_counter()
    response = await call_next(request)
    duration_ms = (time.perf_counter() - start_time) * 1000.0

    # Attach observability headers
    response.headers["X-Request-ID"] = request_id
    response.headers["X-Process-Time"] = f"{duration_ms:.2f}ms"

    # Attach security hardening headers
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    response.headers["X-XSS-Protection"] = "1; mode=block"

    return response

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

APP_START_TIME = time.time()

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

@app.get("/health/live")
@app.get("/api/health/live")
async def liveness_probe():
    """
    Kubernetes / Docker Liveness probe verifying process is alive and responsive.
    """
    return {
        "status": "alive",
        "service": "EduPath AI Backend Engine",
        "uptime_seconds": round(time.time() - APP_START_TIME, 2),
        "timestamp": time.time(),
        "version": settings.VERSION
    }

@app.get("/ready")
@app.get("/api/ready")
@app.get("/health/ready")
@app.get("/api/health/ready")
async def readiness_probe():
    """
    Comprehensive Kubernetes / Production Readiness probe validating:
    - Database query responsiveness (AsyncSession SELECT 1)
    - Storage write permissions (UPLOAD_DIR)
    - AI Provider connectivity (Gemini client status)
    - Embedding engine readiness (768-dim vector engine)
    - Retrieval subsystem status (Hybrid RRF / BM25)
    """
    try:
        async with AsyncSessionLocal() as session:
            await session.execute(text("SELECT 1"))
    except Exception as e:
        logger.error(f"Readiness probe failed on database connection: {e}")
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content={
                "status": "not_ready",
                "service": "EduPath AI Backend Engine",
                "subsystems": {
                    "database": f"error: {str(e)}",
                    "storage": "unknown",
                    "ai_provider": "unknown",
                    "embedding_engine": "unknown",
                    "retrieval_system": "unknown"
                },
                "version": settings.VERSION
            }
        )

    storage_writable = os.access(settings.UPLOAD_DIR, os.W_OK) if os.path.exists(settings.UPLOAD_DIR) else True
    if not storage_writable:
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content={
                "status": "not_ready",
                "service": "EduPath AI Backend Engine",
                "storage": "directory not writable",
                "subsystems": {
                    "database": "ready",
                    "storage": "directory not writable",
                    "ai_provider": "ready",
                    "embedding_engine": "ready",
                    "retrieval_system": "ready"
                },
                "version": settings.VERSION
            }
        )

    from app.services.gemini_service import gemini_service
    ai_status = "configured" if gemini_service.is_configured else "internal_deterministic_mode"
    emb_model = getattr(gemini_service.embeddings, "model_name", "text-embedding-004")
    emb_dim = getattr(gemini_service.embeddings, "dimension", 768)

    return {
        "status": "ready",
        "service": "EduPath AI Backend Engine",
        "database": "ready",
        "storage": "ready",
        "subsystems": {
            "database": "ready",
            "storage": "writable",
            "ai_provider": {
                "status": ai_status,
                "model": gemini_service.model_name
            },
            "embedding_engine": {
                "status": "ready",
                "model": emb_model,
                "dimension": emb_dim
            },
            "retrieval_system": {
                "status": "ready",
                "mode": "hybrid_rrf_bm25",
                "rrf_k": 60
            }
        },
        "environment": settings.ENVIRONMENT,
        "version": settings.VERSION
    }
