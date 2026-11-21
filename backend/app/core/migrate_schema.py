import sqlite3
import os

def migrate_database():
    db_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "edupath.db")
    print(f"Migrating SQLite DB at: {db_path}")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    def add_col_if_missing(table, col, col_def):
        cursor.execute(f"PRAGMA table_info({table})")
        cols = [r[1] for r in cursor.fetchall()]
        if col not in cols:
            cursor.execute(f"ALTER TABLE {table} ADD COLUMN {col} {col_def}")
            print(f"  [+] Added {col} to {table}")
        else:
            print(f"  [.] {col} already exists in {table}")

    # Subject columns
    add_col_if_missing('subjects', 'category', "VARCHAR(100) DEFAULT 'Computer Science'")
    add_col_if_missing('subjects', 'icon_name', "VARCHAR(50) DEFAULT 'BookOpen'")

    # Topic columns
    add_col_if_missing('topics', 'module_name', "VARCHAR(255) DEFAULT 'Module 1: Foundations'")
    add_col_if_missing('topics', 'subtopics_json', "TEXT")
    add_col_if_missing('topics', 'is_emerging', "BOOLEAN DEFAULT 0")
    add_col_if_missing('topics', 'source_reference', "VARCHAR(512)")
    add_col_if_missing('topics', 'last_updated_date', "VARCHAR(50)")

    # Question columns
    add_col_if_missing('questions', 'code_snippet', "TEXT")
    add_col_if_missing('questions', 'test_cases_json', "TEXT")

    conn.commit()
    conn.close()
    print("Schema migration complete.")

if __name__ == "__main__":
    migrate_database()
