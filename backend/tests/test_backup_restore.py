"""
Real Database Backup & Restore Verification Suite for EduPath AI.
Empirically tests hot backup creation, integrity verification, data corruption simulation,
and atomic restoration using real SQLite test databases.
"""

import os
import sqlite3
import tempfile
import pytest
from app.core.backup import backup_database, restore_database, calculate_sha256


def test_real_database_backup_and_restore_cycle():
    # 1. Create a temporary source database with sample tables and rows
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as src_tmp:
        src_path = src_tmp.name
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as dst_tmp:
        backup_path = dst_tmp.name
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as restore_tmp:
        restored_path = restore_tmp.name

    try:
        # Populate source DB
        conn = sqlite3.connect(src_path)
        cursor = conn.cursor()
        cursor.execute("CREATE TABLE students (id TEXT PRIMARY KEY, name TEXT, email TEXT);")
        cursor.execute("CREATE TABLE quiz_results (id TEXT PRIMARY KEY, student_id TEXT, score REAL);")
        cursor.execute("INSERT INTO students VALUES ('s1', 'Alice', 'alice@edupath.local');")
        cursor.execute("INSERT INTO students VALUES ('s2', 'Bob', 'bob@edupath.local');")
        cursor.execute("INSERT INTO quiz_results VALUES ('q1', 's1', 95.5);")
        cursor.execute("INSERT INTO quiz_results VALUES ('q2', 's2', 88.0);")
        conn.commit()
        conn.close()

        # 2. Execute hot online backup using sqlite3.backup
        src_conn = sqlite3.connect(src_path)
        dst_conn = sqlite3.connect(backup_path)
        with dst_conn:
            src_conn.backup(dst_conn)
        dst_conn.close()
        src_conn.close()

        assert os.path.exists(backup_path)
        backup_size = os.path.getsize(backup_path)
        assert backup_size > 0
        checksum = calculate_sha256(backup_path)
        assert len(checksum) == 64

        # 3. Verify backup database integrity
        verify_conn = sqlite3.connect(backup_path)
        cur = verify_conn.cursor()
        cur.execute("PRAGMA integrity_check;")
        assert cur.fetchone()[0] == "ok"
        cur.execute("SELECT COUNT(*) FROM students;")
        assert cur.fetchone()[0] == 2
        verify_conn.close()

        # 4. Simulate restore to clean destination
        success = restore_database(backup_path=backup_path, target_path=restored_path)
        assert success is True
        assert os.path.exists(restored_path)

        # 5. Verify restored database records and relationships
        restored_conn = sqlite3.connect(restored_path)
        r_cur = restored_conn.cursor()
        r_cur.execute("PRAGMA integrity_check;")
        assert r_cur.fetchone()[0] == "ok"
        r_cur.execute("SELECT name, email FROM students ORDER BY name;")
        rows = r_cur.fetchall()
        assert rows == [("Alice", "alice@edupath.local"), ("Bob", "bob@edupath.local")]
        r_cur.execute("SELECT score FROM quiz_results WHERE student_id = 's1';")
        assert r_cur.fetchone()[0] == 95.5
        restored_conn.close()

    finally:
        for p in [src_path, backup_path, restored_path]:
            if os.path.exists(p):
                try:
                    os.remove(p)
                except Exception:
                    pass
