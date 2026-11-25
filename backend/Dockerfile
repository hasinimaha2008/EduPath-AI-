# ==============================================================================
# EduPath AI - Production Backend Multi-Stage Dockerfile
# Python 3.11 FastAPI with minimal runtime, non-root security & live healthchecks
# ==============================================================================

# ------------------------------------------------------------------------------
# Stage 1: Build Dependencies & Wheels
# ------------------------------------------------------------------------------
FROM python:3.11-slim AS builder

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

WORKDIR /build

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip wheel --no-cache-dir --wheel-dir /build/wheels -r requirements.txt

# ------------------------------------------------------------------------------
# Stage 2: Production Minimal Runtime
# ------------------------------------------------------------------------------
FROM python:3.11-slim AS runner

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PORT=8000 \
    ENVIRONMENT=production

WORKDIR /app

# Install minimal runtime dependencies (curl for container orchestrator health checks)
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Create dedicated non-root application user and group
RUN groupadd -g 10001 edupath && \
    useradd -u 10001 -g edupath -s /bin/bash -m edupath

# Install wheels built in builder stage
COPY --from=builder /build/wheels /wheels
RUN pip install --no-cache-dir /wheels/* && rm -rf /wheels

# Create required runtime directories with non-root ownership
RUN mkdir -p /app/uploads /app/backups /app/data && \
    chown -R edupath:edupath /app

# Copy application source code
COPY --chown=edupath:edupath . /app

USER edupath

EXPOSE 8000

# Container liveness probe for Docker / Kubernetes
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD curl -f http://localhost:8000/api/health/live || exit 1

# Production ASGI server launch
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
