"""
EduPath AI - Automated Database Migration Lifecycle & Safety Tests
Verifies Alembic schema migrations: clean upgrade to head, schema inspection,
downgrade to base, and re-upgrade resilience on an isolated SQLite database.
"""

import os
import pytest
from sqlalchemy import create_engine, inspect
from alembic.config import Config
from alembic import command


@pytest.fixture
def temp_alembic_env(tmp_path, monkeypatch):
    """Provides an isolated database environment for migration testing."""
    test_db_path = tmp_path / "migration_test.db"
    sync_url = f"sqlite:///{test_db_path.as_posix()}"
    async_url = f"sqlite+aiosqlite:///{test_db_path.as_posix()}"

    # Override settings DATABASE_URL
    from app.core.config import settings
    monkeypatch.setattr(settings, "DATABASE_URL", async_url)

    # Prepare Alembic Config
    backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    ini_path = os.path.join(backend_dir, "alembic.ini")
    alembic_cfg = Config(ini_path)
    alembic_cfg.set_main_option("script_location", os.path.join(backend_dir, "alembic"))

    return {
        "sync_url": sync_url,
        "db_path": test_db_path,
        "alembic_cfg": alembic_cfg,
    }


def test_alembic_migration_upgrade_and_downgrade_cycle(temp_alembic_env):
    """
    Validates:
    1. Fresh database upgrade to head
    2. Verification that all required core tables are created
    3. Downgrade to base
    4. Re-upgrade to head without corruption
    """
    alembic_cfg = temp_alembic_env["alembic_cfg"]
    sync_url = temp_alembic_env["sync_url"]

    # Step 1: Upgrade to head
    command.upgrade(alembic_cfg, "head")

    engine = create_engine(sync_url)
    inspector = inspect(engine)
    tables = inspector.get_table_names()

    # Verify expected tables exist
    expected_tables = {
        "users",
        "documents",
        "document_chunks",
        "conversations",
        "chat_messages",
        "quizzes",
        "questions",
        "quiz_attempts",
        "notes",
        "subjects",
        "topics",
        "study_plans",
        "alembic_version",
    }
    assert expected_tables.issubset(set(tables)), f"Missing tables after upgrade: {expected_tables - set(tables)}"

    # Step 2: Downgrade to base
    command.downgrade(alembic_cfg, "base")

    inspector_after_downgrade = inspect(engine)
    tables_after = inspector_after_downgrade.get_table_names()
    # Core application tables should be dropped after downgrade to base
    assert "users" not in tables_after, "Expected 'users' table to be dropped after downgrade to base"

    # Step 3: Re-upgrade to head (idempotency & failure recovery test)
    command.upgrade(alembic_cfg, "head")
    inspector_reup = inspect(engine)
    reup_tables = inspector_reup.get_table_names()
    assert expected_tables.issubset(set(reup_tables)), "Re-upgrade after downgrade failed to recreate all tables"

    engine.dispose()
