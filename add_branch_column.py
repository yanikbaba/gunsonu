
# add_branch_column.py — one-off helper (idempotent)
import sqlite3, sys

def add_branch(db_path: str) -> None:
    con = sqlite3.connect(db_path)
    try:
        cols = [r[1] for r in con.execute("PRAGMA table_info(expenses)")]
        if "branch" not in cols:
            con.execute("ALTER TABLE expenses ADD COLUMN branch TEXT DEFAULT ''")
            con.commit()
            print("[OK] branch column added")
        else:
            print("[SKIP] branch already exists")
    finally:
        con.close()

if __name__ == "__main__":
    db = sys.argv[1] if len(sys.argv) > 1 else "gunsonu.sqlite"
    add_branch(db)
