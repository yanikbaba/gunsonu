# GunSonu DB migrations v4-final
# idempotent, strip-safe, default-detection-stable

import sqlite3
from typing import List, Tuple

# DB schema versioning table (if not exists)
SCHEMA_VERSION_TABLE = """
CREATE TABLE IF NOT EXISTS schema_version (
    version INTEGER NOT NULL
)
"""

def get_version(con: sqlite3.Connection) -> int:
    cur = con.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='schema_version'")
    if cur.fetchone() is None:
        con.execute("INSERT OR IGNORE INTO schema_version(version) VALUES(1)")
        return 1
    row = con.execute("SELECT version FROM schema_version").fetchone()
    return row[0] if row else 1

def bump_version(con: sqlite3.Connection, v: int) -> None:
    con.execute("UPDATE schema_version SET version=?", (v,))
    con.commit()

# ----- Utility -----

def _columns(con, table: str) -> List[Tuple]:
    return con.execute(f"PRAGMA table_info({table})").fetchall()

def column_exists(con, table: str, col: str) -> bool:
    return any(row[1] == col for row in _columns(con, table))

def _is_empty_default(dflt: str | None) -> bool:
    if dflt is None:
        return False
    stripped = dflt.strip("'")    # *** final corrected ***
    return stripped == ""

# ----- MIGRATIONS -----

def migrate_v2(con):
    # add expenses.branch
    if not column_exists(con, "expenses", "branch"):
        con.execute("ALTER TABLE expenses ADD COLUMN branch TEXT DEFAULT '' NOT NULL")
    con.commit()

def migrate_v3(con):
    # add expenses.category
    if not column_exists(con, "expenses", "category"):
        con.execute("ALTER TABLE expenses ADD COLUMN category TEXT DEFAULT '' NOT NULL")
    con.commit()

def migrate_v4(con):
    # enforce defaults compatibility (no-op for now)
    # ensure NOT NULL compatible behavior
    rows = con.execute("PRAGMA table_info(expenses)").fetchall()
    for cid, name, ctype, notnull, dflt_value, pk in rows:
        if name in ("branch", "category") and notnull and _is_empty_default(dflt_value):
            # Already normalized
            pass
    con.commit()

# ----- ROUTER -----

def migrate(con):
    v = get_version(con)

    if v < 2:
        migrate_v2(con); bump_version(con, 2)
        v = 2
    if v < 3:
        migrate_v3(con); bump_version(con, 3)
        v = 3
    if v < 4:
        migrate_v4(con); bump_version(con, 4)
        v = 4

def run(db_path: str):
    con = sqlite3.connect(db_path)
    con.execute(SCHEMA_VERSION_TABLE)
    migrate(con)
    con.close()

if __name__ == "__main__":
    import sys
    db = sys.argv[1] if len(sys.argv) > 1 else "gunsonu.sqlite"
    run(db)
    print("[OK] DB migrated to version 4")
