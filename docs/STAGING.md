# EduPath AI – Staging Environment Deployment & Operations

**Document Version:** 2.0.0-production  
**Author:** Principal DevOps & Cloud Architect  
**Workflow:** `.github/workflows/deploy-staging.yml`  

---

## 1. Staging Purpose & Environment Specification

The staging environment mirrors production architecture to validate application integration, database migrations, container interoperability, and AI model interactions prior to production promotion.

```mermaid
flowchart LR
    Push["Push to master/main"] --> Validate["Pre-Deploy Validation\n(alembic check)"]
    Validate --> Deploy["Rolling Container Update\n(GHCR Images)"]
    Deploy --> Ready["Wait for Application Readiness\n(/api/health/ready)"]
    Ready --> Smoke["Automated Smoke Test Runner\n(backend/tests/smoke_test.py)"]
    Smoke -->|Success| Active["Staging Active & Ready for QA"]
    Smoke -->|Failure| Alert["Alert & Abort Release Promotion"]
```

---

## 2. Staging Configuration & Secrets

Configure the following secrets in GitHub under **Environments > staging**:

| Secret Name | Purpose | Example Value |
|---|---|---|
| `STAGING_API_URL` | Target endpoint for post-deployment smoke tests | `https://staging-api.yourdomain.com` |
| `DATABASE_URL` | Staging database connection string | `postgresql+asyncpg://user:pass@host:5432/edupath_staging` |
| `JWT_SECRET` | Cryptographic key for staging JWT tokens | `staging_secret_key_minimum_32_characters` |
| `GEMINI_API_KEY` | Google Gemini API key for staging AI inference | `AIzaSy...` |

---

## 3. Staging Deployment Pipeline Steps

The [`deploy-staging.yml`](file:///.github/workflows/deploy-staging.yml) workflow executes automatically on pushes to `master` and `main`:

1. **Pre-Deployment Migration Check**:
   Executes `python -m alembic check` to ensure migration heads are synchronized with database models.
2. **Container Image Rollout**:
   Deploys immutable images tagged with `sha-${GITHUB_SHA::8}` from GHCR.
3. **Readiness Probe Polling**:
   Polls `/api/health/ready` until all 5 subsystems (`database`, `storage`, `ai_provider`, `embedding_engine`, `retrieval_system`) report healthy.
4. **Automated Smoke Testing**:
   Executes `python backend/tests/smoke_test.py --url "$STAGING_API_URL"`, running 8 end-to-end tests:
   - Basic Health Probe (`/health`)
   - Liveness Probe (`/api/health/live`)
   - Readiness Subsystem Probe (`/api/health/ready`)
   - Catalog Taxonomy (`/api/subjects`)
   - Career Intelligence Roles (`/api/careers/roles`)
   - User Registration & JWT Issuance (`/api/auth/register`)
   - Authenticated User Profile (`/api/auth/me`)
   - AI Study Assistant Grounded Reasoning (`/api/assistant/ask`)

---

## 4. Manual Staging Verification & Troubleshooting

To execute smoke tests against staging manually from your workstation:
```bash
python backend/tests/smoke_test.py --url https://staging-api.yourdomain.com
```

If staging fails:
1. Inspect container logs:
   ```bash
   docker logs edupath-backend
   ```
2. Verify database migration status:
   ```bash
   alembic current
   ```
