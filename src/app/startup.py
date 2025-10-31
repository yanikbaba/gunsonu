# src/app/startup.py — with v6 migration support
from pathlib import Path
import sqlite3
from typing import Optional

MIGRATIONS_DIR = Path(__file__).resolve().parents[2] / "db_migrations"

def _ensure_meta(db):
    db.execute("CREATE TABLE IF NOT EXISTS meta (key TEXT PRIMARY KEY, value TEXT)")
    cur = db.execute("SELECT value FROM meta WHERE key='schema_version'")
    row = cur.fetchone()
    if not row:
        db.execute("INSERT OR REPLACE INTO meta(key,value) VALUES ('schema_version','4')")

def _current_version(db) -> int:
    cur = db.execute("SELECT value FROM meta WHERE key='schema_version'")
    row = cur.fetchone()
    return int(row[0]) if row else 0

def _apply_sql(db, sql_text: str):
    db.executescript(sql_text)

def run_auto_migrations(db_path: str, migrations_dir: Optional[str] = None) -> int:
    mig_dir = Path(migrations_dir) if migrations_dir else MIGRATIONS_DIR
    db = sqlite3.connect(db_path)
    try:
        _ensure_meta(db)
        current = _current_version(db)

        mig_004 = mig_dir / "004_create_advances.sql"
        if current < 5 and mig_004.exists():
            _apply_sql(db, mig_004.read_text(encoding="utf-8"))
            current = _current_version(db)

        mig_005 = mig_dir / "005_create_z_report.sql"
        if current < 6 and mig_005.exists():
            _apply_sql(db, mig_005.read_text(encoding="utf-8"))

        db.commit()
        return _current_version(db)
    finally:
        db.close()

def on_app_start(db_path: str = "gunsonu.sqlite") -> int:
    return run_auto_migrations(db_path)