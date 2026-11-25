# EduPath AI – Database Migration Architecture & Safety

**Document Version:** 2.0.0-production  
**Author:** Principal Database Reliability Engineer  
**Component:** `backend/alembic` & `backend/tests/test_migrations.py`  

---

## 1. Migration Philosophy: Zero Data Loss

EduPath AI uses **Alembic** alongside SQLAlchemy ORM models to manage database schema evolution. In high-availability production, migrations must never lock tables for extended periods or drop active columns before older container instances have terminated.

### The Expand-and-Contract Pattern
```text
Phase 1 (Expand):
  Add new columns / tables with default values or NULL constraints.
  Alembic upgrade head is applied. Both old and new application versions function cleanly.

Phase 2 (Migrate):
  Deploy new application version. Background tasks populate newly added columns.

Phase 3 (Contract):
  After verifying all traffic routes to new code, a subsequent migration removes obsolete columns.
```

---

## 2. Directory Structure & Version Tracking

```text
backend/
├── alembic.ini                   # Alembic configuration
├── alembic/
│   ├── env.py                    # Sync engine adapter for async dialects
│   ├── script.py.mako            # Migration template
│   └── versions/
│       └── ace91d80022d_initial_schema.py   # Base migration
└── tests/
    └── test_migrations.py        # Automated migration lifecycle test
```

---

## 3. Automated Migration Testing in CI

To ensure no pull request introduces broken migrations, `backend/tests/test_migrations.py` runs during every CI build:
- Creates an isolated temporary SQLite database.
- Executes `alembic upgrade head`.
- Verifies that all 13 core tables exist (`users`, `documents`, `document_chunks`, `conversations`, `chat_messages`, `quizzes`, `questions`, `quiz_attempts`, `notes`, `subjects`, `topics`, `study_plans`, `alembic_version`).
- Executes `alembic downgrade base` and verifies clean table teardown.
- Re-executes `alembic upgrade head` to verify idempotency and failure recovery.

---

## 4. Local Migration Commands

```bash
# 1. Generate a new auto-detected migration
cd backend
alembic revision --autogenerate -m "add_student_badges_table"

# 2. Check current database revision
alembic current

# 3. Apply all pending migrations to head
alembic upgrade head

# 4. Rollback one revision (Staging/Dev only)
alembic downgrade -1
```

> [!CAUTION]
> Never execute `alembic downgrade` in production without verifying that dependent application code has already been reverted. Always consult `docs/ROLLBACK.md` before applying schema rollbacks.
