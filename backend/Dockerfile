# ==============================================================================
# EduPath AI - Production Backend Dockerfile
# Python 3.11 FastAPI with non-root security execution and health checks
# ==============================================================================

FROM python:3.11-slim as base

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PORT=8000

WORKDIR /app

# Install system dependencies (build tools for compilation if needed)
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Install Python requirements
COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Create application uploads directory and non-root execution user
RUN useradd -m -u 1001 edupath && \
    mkdir -p /app/uploads && \
    chown -R edupath:edupath /app

# Copy application source code
COPY --chown=edupath:edupath . /app

USER edupath

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
