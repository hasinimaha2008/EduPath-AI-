# EduPath AI – Production Operations & CD Handbook

**Document Version:** 2.0.0-production  
**Author:** Principal SRE & Release Architect  
**Workflow:** `.github/workflows/deploy-production.yml`  

---

## 1. Production Architecture Overview

The production environment provides zero-downtime availability, strict tenant isolation, authenticated caching, and automated rollbacks upon health degradation.

```mermaid
flowchart TD
    Release["GitHub Release Published / Manual Dispatch"] --> Approval{"Manual Approval Gate\n(GitHub Environments: production)"}
    Approval -->|Approved| PreBackup["Pre-Deploy Atomic DB Backup\n(SHA256 sidecar generated)"]
    PreBackup --> Migrate["Forward-Compatible Alembic Upgrade\n(alembic upgrade head)"]
    Migrate --> RollingDeploy["Zero-Downtime Rolling Container Update\n(ghcr.io/hasinimaha2008/...:sha-xxxx)"]
    RollingDeploy --> HealthGate{"Post-Deploy Smoke Gate\n(tests/smoke_test.py)"}
    HealthGate -->|Pass (100%)| ProductionActive["Production Active & Monitored"]
    HealthGate -->|Fail| EmergencyRollback["Trigger docs/ROLLBACK.md\nRestore Container & Database"]
```

---

## 2. Production Environment Protection & Approvals

1. **GitHub Environment**: Configured under **Settings > Environments > production**.
2. **Required Reviewers**: Requires manual authorization by designated Release Managers or Lead Engineers.
3. **Branch Restriction**: Deployments are permitted exclusively from release tags (`v*.*.*`) or `master`/`main`.
4. **Concurrency Lockdown**: Only one production deployment job executes at any given time (`concurrency: group: deploy-production`).

---

## 3. Mandatory Production Secrets

| Secret Name | Description | Verification Constraint |
|---|---|---|
| `PRODUCTION_API_URL` | Live API Gateway URL | Must be HTTPS with valid TLS certificate |
| `DATABASE_URL` | Production PostgreSQL connection string | `postgresql+asyncpg://...` (SSL mode enabled) |
| `JWT_SECRET` | 32+ character HMAC-SHA256 signing secret | Reject defaults; generated via `openssl rand -hex 32` |
| `GEMINI_API_KEY` | Google Gemini API key | Active AI Studio key with appropriate RPM tier |
| `REDIS_PASSWORD` | Strong Redis authentication secret | Must be non-empty in `docker-compose.prod.yml` |
| `ALLOWED_ORIGINS` | Strict CORS permitted origin whitelist | `https://edupath.yourdomain.com` (no wildcards) |

---

## 4. Zero-Downtime Deployment Procedure

### Step 1: Pre-Deployment Backup
Before modifying any state, the database engine creates a snapshot with an accompanying cryptographic SHA256 sidecar:
```bash
python -m app.services.database.backup_service --create --dest /app/backups/
```

### Step 2: Apply Database Migrations
Migrations apply forward-compatible schema changes:
```bash
alembic upgrade head
```

### Step 3: Rolling Container Update
Containers update using immutable SHA tags:
```bash
docker compose -f docker-compose.prod.yml pull
docker compose -f docker-compose.prod.yml up -d --no-deps backend
docker compose -f docker-compose.prod.yml up -d --no-deps frontend
```

### Step 4: Post-Deploy Verification Gate
Automated smoke test runs against the production gateway:
```bash
python backend/tests/smoke_test.py --url https://api.yourdomain.com
```

If the smoke test reports any failure, the workflow initiates the rollback runbook in [`docs/ROLLBACK.md`](file:///docs/ROLLBACK.md).
