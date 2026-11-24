"""
EduPath AI - Production Database Backup & Restore Utility.
Provides zero-downtime hot backups and atomic restoration for SQLite and PostgreSQL.
"""

import os
import sys
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
        logger.info(f"PostgreSQL backup completed: {destination_path} ({size} bytes)")
        return destination_path, checksum, size

    else:
        raise NotImplementedError(f"Unsupported database dialect for backup: {db_url}")


def restore_database(backup_path: str, target_path: Optional[str] = None) -> bool:
    """
    Safely restores the database from a verified backup archive.
    Ensures atomic replacement with rollback recovery on corrupt or failing archives.
    """
    if not os.path.exists(backup_path):
        raise FileNotFoundError(f"Specified backup file does not exist: {backup_path}")

    db_url = settings.DATABASE_URL
    is_sqlite = (target_path and target_path.endswith(".db")) or ("sqlite" in db_url)

    if is_sqlite:
        dest_path = os.path.abspath(target_path) if target_path else get_sqlite_db_path()
        if not dest_path:
            raise ValueError("Target database path could not be determined.")

        # Verify integrity of backup before restoring
        verify_conn = sqlite3.connect(backup_path)
        cursor = verify_conn.cursor()
        cursor.execute("PRAGMA integrity_check;")
        res = cursor.fetchone()
        verify_conn.close()
        if not res or res[0] != "ok":
            raise ValueError(f"Cannot restore from corrupt backup: {res}")

        # Atomic copy and swap with cleanup
        temp_dest = dest_path + ".restore.tmp"
        try:
            shutil.copy2(backup_path, temp_dest)
            if os.path.exists(dest_path):
                os.replace(temp_dest, dest_path)
            else:
                os.rename(temp_dest, dest_path)
        finally:
            if os.path.exists(temp_dest):
                try:
                    os.remove(temp_dest)
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
