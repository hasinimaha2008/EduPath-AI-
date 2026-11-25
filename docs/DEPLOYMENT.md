# EduPath AI — Production Deployment Guide

## 1. Overview

EduPath AI is architected for reliable, single-command deployment via Docker Compose or modular deployment on bare-metal and cloud virtual machines (AWS EC2, GCP Compute Engine, Azure VMs, Railway, Render, Fly.io).

---

## 2. Production Architecture

```mermaid
flowchart TD
    Client["Client Browsers / Mobile Viewports"] --> ReverseProxy["Reverse Proxy (Nginx / Caddy / Cloudflare)\nHTTPS :443 Termination"]
    
    subgraph DockerCompose["Docker Multi-Container Network (docker-compose.yml)"]
        ReverseProxy -->|Proxy /api/*| Backend["FastAPI Backend Container\nPython 3.11-slim (Port 8000)\nUser: edupath (UID 1001)"]
        ReverseProxy -->|Proxy /*| Frontend["Next.js 14 Frontend Container\nNode 20-alpine (Port 3000)\nUser: nextjs (UID 1001)"]
        
        Backend <-->|Rate Limit & Cache| Redis["Redis 7 Alpine Container\nPort 6379 (Volume: redis-data)"]
        Backend <-->|App Data & Vectors| DB[("Database Storage\nSQLite Local (Volume: backend-db)\nor Supabase PostgreSQL")]
        Backend <-->|Upload Storage| Uploads[("Encrypted File Storage\nVolume: backend-uploads")]
    end
```

---

## 3. Environment Variables Reference

Create a secure `.env` file in the root directory or configure environment variables in your deployment orchestrator:

| Variable | Required | Default | Description |
|---|:---:|---|---|
| `ENVIRONMENT` | **Yes** | `production` | Target environment (`development`, `staging`, `production`). In production, demo login is restricted. |
| `JWT_SECRET` | **Yes** | — | Cryptographically random string ($\ge 32$ chars) used for HMAC-SHA256 session token signing. |
| `DATABASE_URL` | **Yes** | `sqlite+aiosqlite:////app/edupath.db` | SQLAlchemy connection string. Swappable for `postgresql+asyncpg://user:pass@host:5432/edupath`. |
| `REDIS_URL` | Optional | `redis://redis:6379/0` | Redis instance for sliding-window rate limiting. Falls back to in-memory cache if omitted. |
| `GEMINI_API_KEY` | Optional | — | Google Gemini API key. When omitted, platform runs in verified deterministic pedagogical mode. |
| `ALLOW_DEMO_LOGIN` | Optional | `false` | Explicit toggle to permit `/api/auth/demo-login` in staging/testing environments. |
| `ALLOWED_ORIGINS` | Optional | `http://localhost:3000` | Comma-separated CORS allowed origins. |
| `UPLOAD_DIR` | Optional | `/app/uploads` | Path for uploaded PDF/document chunks and index metadata. |
| `PORT` | Optional | `8000` | Backend API port. |

---

## 4. Single-Command Deployment via Docker Compose

### Prerequisites
- Docker Engine 24.0+
- Docker Compose v2.20+

### Execution Commands
```bash
# 1. Clone repository
git clone https://github.com/hasinimaha2008/EduPath-AI-.git
cd EduPath-AI-

# 2. Configure production secrets
cp .env.example .env
# Edit .env and supply a strong JWT_SECRET (openssl rand -hex 32)

# 3. Build and launch services in detached mode
docker compose up --build -d

# 4. Verify running container health
docker compose ps
```

---

## 5. Manual / Bare-Metal Deployment

### Step A: Database Bootstrap & Migrations
```bash
cd backend
python -m venv .venv
source .venv/bin/activate  # On Windows: .\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
alembic upgrade head
```

### Step B: Launch Backend Service
```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
```

### Step C: Build & Launch Frontend
```bash
cd ../frontend
npm ci
npm run build
npm run start -- -p 3000
```

---

## 6. Post-Deployment Smoke Verification

Run the automated smoke test suite to verify end-to-end operational readiness:

```bash
cd backend
DEPLOYMENT_URL=http://localhost:8000 python tests/smoke_test.py
```
This executes 8 automated checks verifying `/health`, `/health/live`, `/health/ready`, taxonomy, user registration, JWT generation, and grounded AI reasoning.
