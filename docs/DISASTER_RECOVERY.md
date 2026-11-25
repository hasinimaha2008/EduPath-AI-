# EduPath AI – Disaster Recovery & Business Continuity Plan

**Document Version:** 1.0.0-production  
**Author:** Principal Cloud Architect & SRE Lead  
**Classification:** Operational Runbook  

---

## 1. Disaster Recovery Objectives

| Metric | Target SLA | Operational Strategy |
|---|:---:|---|
| **Recovery Time Objective (RTO)** | **$< 15$ minutes** | Containerized redeployment using immutable GHCR images and automated database restoration. |
| **Recovery Point Objective (RPO)** | **$< 1$ hour** | Hourly snapshot backups with offsite object storage synchronization. |
| **Service Availability Target** | **$99.9\%$** | Multi-container Docker / Kubernetes orchestration with automatic failover. |

---

## 2. Disaster Scenarios & Mitigation Runbooks

```mermaid
flowchart TD
    Incident{"Incident Detected"}
    Incident -->|Host Failure / Corruption| DR1["Scenario 1: Host / Database Loss\nProvision New Host + Restore Sidecar Backup"]
    Incident -->|Cloud / AZ Outage| DR2["Scenario 2: Cloud Region Outage\nFailover DNS to Secondary Region"]
    Incident -->|AI Provider Outage| DR3["Scenario 3: External LLM Outage\nActivate Grounded Fallback Engine"]
    Incident -->|Database Lockup| DR4["Scenario 4: SQLite / Postgres Lockup\nTerminate Stalled Queries & Flush WAL"]
```

### Scenario 1: Host Failure or Data Corruption
1. **Provision New Host / Container Instance**:
   ```bash
   git clone https://github.com/hasinimaha2008/EduPath-AI-.git
   cd EduPath-AI-
   git checkout upgrade/production-release
   ```
2. **Retrieve Latest Encrypted Backup from Offsite Storage**:
   ```bash
   aws s3 cp s3://edupath-backups-vault/latest/db_backup.db backend/backups/
   aws s3 cp s3://edupath-backups-vault/latest/db_backup.json backend/backups/
   ```
3. **Verify Integrity & Restore**:
   ```bash
   python -m app.services.database.backup_service --restore backend/backups/db_backup.db
   ```
4. **Launch Application with Isolated Compose**:
   ```bash
   docker compose -f docker-compose.prod.yml up -d
   ```
5. **Verify Subsystems via Smoke Test**:
   ```bash
   python backend/tests/smoke_test.py --url http://127.0.0.1:8000
   ```

---

### Scenario 2: Cloud Provider or Availability Zone Outage
1. **DNS Failover**: Update Cloudflare / Route53 DNS CNAME records to route traffic to the standby secondary cluster.
2. **Sync Uploads & Assets**: Replicate `/app/uploads` volume from replica storage bucket.
3. **Promote Standby Database**: If using Supabase / RDS PostgreSQL, trigger read-replica promotion to primary.

---

### Scenario 3: External AI Provider (Google Gemini) Outage
When the external LLM provider experiences quota exhaustion or outage:
1. The platform automatically activates its **deterministic fallback engine**:
   - Explanation requests yield structured pedagogical explanations with citations.
   - Quizzes generate from local database topic taxonomies without unhandled exceptions.
   - Student progress and mastery analytics continue tracking uninterrupted.
2. **Switching Provider Key**:
   Update `GEMINI_API_KEY` in `backend/.env` and trigger graceful reload:
   ```bash
   docker compose kill -s SIGHUP backend
   ```

---

### Scenario 4: SQLite WAL Concurrency Lock
If high concurrent write traffic creates a lock timeout on SQLite:
1. Inspect running transactions:
   ```bash
   sqlite3 backend/edupath.db "PRAGMA wal_checkpoint(TRUNCATE);"
   ```
2. For permanent multi-user concurrency ($\ge 50$ concurrent writers), switch backend to PostgreSQL:
   ```bash
   DATABASE_URL="postgresql+asyncpg://user:password@pg-host:5432/edupath"
   ```
   Alembic migrations apply automatically on startup (`alembic upgrade head`).

---

## 3. Disaster Recovery Testing Cadence

1. **Automated Weekly Restore Drill**:
   - The `.github/workflows/scheduled-maintenance.yml` workflow runs every Sunday at 02:00 UTC.
   - Automatically executes `backend/tests/test_backup_restore.py`, verifying tamper detection and clean restoration.
2. **Quarterly Simulated Regional Failover**:
   - Standby cluster spins up from cold storage.
   - Smoke test suite validates all 8 critical operational subsystems.
