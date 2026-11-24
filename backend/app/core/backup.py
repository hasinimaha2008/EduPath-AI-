"""
EduPath AI - Production Database Backup & Restore Utility.
Provides zero-downtime hot backups and atomic restoration for SQLite and PostgreSQL.
"""

import os
import sys
import json
import shutil
import sqlite3
import hashlib
import logging
import argparse
from datetime import datetime, timezone
from typing import Optional, Tuple
from app.core.config import settings

logger = logging.getLogger("edupath.backup")
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")


def calculate_sha256(file_path: str) -> str:
    """Computes SHA256 checksum for backup integrity verification."""
    sha256 = hashlib.sha256()
    with open(file_path, "rb") as f:
        while chunk := f.read(65536):
            sha256.update(chunk)
    return sha256.hexdigest()


def get_sqlite_db_path() -> Optional[str]:
    """Extracts raw filesystem path from settings.DATABASE_URL if SQLite."""
    url = settings.DATABASE_URL
    if "sqlite" in url:
        # Format: sqlite+aiosqlite:///./edupath.db or sqlite:///./edupath.db
        cleaned = url.split(":///")[-1]
        return os.path.abspath(cleaned)
    return None


def backup_database(destination_path: Optional[str] = None, source_path: Optional[str] = None) -> Tuple[str, str, int]:
    """
    Executes an atomic online hot-backup of the database.
    Returns: (backup_file_path, sha256_checksum, file_size_bytes)
    """
    db_url = settings.DATABASE_URL
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")

    # Determine if SQLite based on source_path or db_url
    is_sqlite = (source_path and source_path.endswith(".db")) or ("sqlite" in db_url)

    # 1. SQLite Hot Online Backup (zero lock, production safe)
    if is_sqlite:
        src_path = os.path.abspath(source_path) if source_path else get_sqlite_db_path()
        if not src_path or not os.path.exists(src_path):
            raise FileNotFoundError(f"Source database file not found at: {src_path}")

        if not destination_path:
            backup_dir = os.path.join(os.path.dirname(src_path), "backups")
            os.makedirs(backup_dir, exist_ok=True)
            destination_path = os.path.join(backup_dir, f"edupath_backup_{timestamp}.db")
        else:
            os.makedirs(os.path.dirname(os.path.abspath(destination_path)), exist_ok=True)

        logger.info(f"Starting SQLite online hot backup from '{src_path}' to '{destination_path}'...")
        src_conn = sqlite3.connect(src_path)
        dst_conn = sqlite3.connect(destination_path)

        with dst_conn:
            src_conn.backup(dst_conn, pages=100, sleep=0.01)

        dst_conn.close()
        src_conn.close()

        # Integrity verification
        verify_conn = sqlite3.connect(destination_path)
        cursor = verify_conn.cursor()
        cursor.execute("PRAGMA integrity_check;")
        check_result = cursor.fetchone()
        verify_conn.close()

        if not check_result or check_result[0] != "ok":
            if os.path.exists(destination_path):
                os.remove(destination_path)
            raise ValueError(f"Backup integrity check failed: {check_result}")

        size = os.path.getsize(destination_path)
        checksum = calculate_sha256(destination_path)

        # Extract table statistics for metadata sidecar
        tables = []
        try:
            stat_conn = sqlite3.connect(destination_path)
            cur = stat_conn.cursor()
            cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%';")
            tables = [row[0] for row in cur.fetchall()]
            stat_conn.close()
        except Exception as e:
            logger.warning(f"Could not extract table statistics for metadata: {e}")

        # Produce structured metadata sidecar
        meta_path = destination_path + ".meta.json"
        try:
            with open(meta_path, "w", encoding="utf-8") as mf:
                json.dump({
                    "timestamp": timestamp,
                    "source_path": src_path,
                    "backup_path": destination_path,
                    "sha256": checksum,
                    "size_bytes": size,
                    "table_count": len(tables),
                    "tables": tables,
                    "integrity_status": "ok",
                    "dialect": "sqlite"
                }, mf, indent=2)
        except Exception as e:
            logger.warning(f"Could not write metadata sidecar: {e}")

        logger.info(f"Backup completed successfully: {destination_path} ({size} bytes, SHA256: {checksum[:12]}...)")
        return destination_path, checksum, size

    # 2. PostgreSQL Enterprise Backup
    elif "postgresql" in db_url:
        import subprocess
        if not destination_path:
            destination_path = f"./backups/edupath_pg_{timestamp}.sql"
        os.makedirs(os.path.dirname(os.path.abspath(destination_path)), exist_ok=True)

        logger.info(f"Executing pg_dump for PostgreSQL to '{destination_path}'...")
        cmd = ["pg_dump", db_url, "-f", destination_path]
        res = subprocess.run(cmd, capture_output=True, text=True)
        if res.returncode != 0:
            raise RuntimeError(f"pg_dump failed: {res.stderr}")

        size = os.path.getsize(destination_path)
        checksum = calculate_sha256(destination_path)

        # Produce metadata sidecar for Postgres
        meta_path = destination_path + ".meta.json"
        try:
            with open(meta_path, "w", encoding="utf-8") as mf:
                json.dump({
                    "timestamp": timestamp,
                    "backup_path": destination_path,
                    "sha256": checksum,
                    "size_bytes": size,
                    "dialect": "postgresql"
                }, mf, indent=2)
        except Exception:
            pass

        logger.info(f"PostgreSQL backup completed: {destination_path} ({size} bytes)")
        return destination_path, checksum, size

    else:
        raise NotImplementedError(f"Unsupported database dialect for backup: {db_url}")


def restore_database(backup_path: str, target_path: Optional[str] = None) -> bool:
    """
    Safely restores the database from a verified backup archive.
    Validates checksum metadata sidecar, pre-checks PRAGMA integrity,
    maintains a pre-restore safety snapshot, and atomically replaces target.
    """
    if not os.path.exists(backup_path):
        raise FileNotFoundError(f"Specified backup file does not exist: {backup_path}")

    # Check for metadata sidecar and verify checksum if available
    meta_path = backup_path + ".meta.json"
    if os.path.exists(meta_path):
        try:
            with open(meta_path, "r", encoding="utf-8") as mf:
                meta = json.load(mf)
                expected_sha = meta.get("sha256")
                if expected_sha:
                    actual_sha = calculate_sha256(backup_path)
                    if actual_sha != expected_sha:
                        raise ValueError(f"Backup SHA256 mismatch against metadata sidecar: expected {expected_sha}, got {actual_sha}")
        except json.JSONDecodeError:
            logger.warning(f"Metadata sidecar at {meta_path} was corrupted; proceeding with PRAGMA check.")

    db_url = settings.DATABASE_URL
    is_sqlite = (target_path and target_path.endswith(".db")) or ("sqlite" in db_url)

    if is_sqlite:
        dest_path = os.path.abspath(target_path) if target_path else get_sqlite_db_path()
        if not dest_path:
            raise ValueError("Target database path could not be determined.")

        # Verify integrity of backup archive BEFORE attempting any restore
        verify_conn = sqlite3.connect(backup_path)
        cursor = verify_conn.cursor()
        cursor.execute("PRAGMA integrity_check;")
        res = cursor.fetchone()
        verify_conn.close()
        if not res or res[0] != "ok":
            raise ValueError(f"Cannot restore from corrupt backup: {res}")

        # Pre-restore safety snapshot to guarantee non-destructive recovery
        safety_snapshot = dest_path + ".safety_pre_restore.bak"
        has_existing_dest = os.path.exists(dest_path)
        if has_existing_dest:
            shutil.copy2(dest_path, safety_snapshot)

        # Atomic copy and swap with cleanup
        temp_dest = dest_path + ".restore.tmp"
        try:
            shutil.copy2(backup_path, temp_dest)
            if has_existing_dest:
                os.replace(temp_dest, dest_path)
            else:
                os.rename(temp_dest, dest_path)

            # Post-restore integrity verification
            post_conn = sqlite3.connect(dest_path)
            post_cur = post_conn.cursor()
            post_cur.execute("PRAGMA integrity_check;")
            post_res = post_cur.fetchone()
            post_conn.close()

            if not post_res or post_res[0] != "ok":
                # Rollback from safety snapshot
                if has_existing_dest and os.path.exists(safety_snapshot):
                    os.replace(safety_snapshot, dest_path)
                raise RuntimeError(f"Post-restore integrity check failed: {post_res}; rolled back cleanly.")

            # On clean success, remove safety snapshot
            if os.path.exists(safety_snapshot):
                try:
                    os.remove(safety_snapshot)
                except Exception:
                    pass

        except Exception:
            # Rollback to safety snapshot if failure occurred
            if has_existing_dest and os.path.exists(safety_snapshot):
                try:
                    os.replace(safety_snapshot, dest_path)
                except Exception:
                    pass
            raise
        finally:
            if os.path.exists(temp_dest):
                try:
                    os.remove(temp_dest)
                except Exception:
                    pass
            if os.path.exists(safety_snapshot):
                try:
                    os.remove(safety_snapshot)
                except Exception:
                    pass

        logger.info(f"Database restored successfully from '{backup_path}' to '{dest_path}'.")
        return True

    elif "postgresql" in db_url:
        import subprocess
        logger.info(f"Restoring PostgreSQL database from '{backup_path}'...")
        cmd = ["psql", db_url, "-f", backup_path]
        run_res = subprocess.run(cmd, capture_output=True, text=True)
        if run_res.returncode != 0:
            raise RuntimeError(f"psql restore failed: {run_res.stderr}")
        logger.info("PostgreSQL restoration completed.")
        return True

    return False


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="EduPath AI Database Backup & Restore Utility")
    subparsers = parser.add_subparsers(dest="command", required=True)

    backup_parser = subparsers.add_parser("backup", help="Create database hot backup")
    backup_parser.add_argument("--dest", type=str, default=None, help="Destination backup file path")

    restore_parser = subparsers.add_parser("restore", help="Restore database from backup")
    restore_parser.add_argument("--source", type=str, required=True, help="Path to backup file")
    restore_parser.add_argument("--target", type=str, default=None, help="Path to target database")

    args = parser.parse_args()

    if args.command == "backup":
        path, csum, sz = backup_database(args.dest)
        print(f"SUCCESS: Backup saved to {path} | Size: {sz} bytes | SHA256: {csum}")
    elif args.command == "restore":
        success = restore_database(args.source, args.target)
        if success:
            print("SUCCESS: Database restored cleanly.")
        else:
            print("FAILED: Restoration aborted.")
            sys.exit(1)
