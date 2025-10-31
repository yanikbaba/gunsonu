#!/usr/bin/env python3
"""
Migration Guard (v0.8.1)
- Validates SQLite user_version against expected value
- Fails fast if behind; prints OK if equal or above (unless --strict)
Usage:
    python src/guards/migration_guard.py --db gunsonu.sqlite --expect 8 --strict
"""
import argparse, sqlite3, os, sys

def get_user_version(db_path: str) -> int:
    con = sqlite3.connect(db_path)
    try:
        cur = con.execute("PRAGMA user_version;")
        row = cur.fetchone()
        return int(row[0] or 0)
    finally:
        con.close()

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--db', default='gunsonu.sqlite')
    ap.add_argument('--expect', type=int, default=8, help='expected schema version')
    ap.add_argument('--strict', action='store_true', help='fail if version is not exactly equal')
    args = ap.parse_args()
    if not os.path.exists(args.db):
        print(f"[guard] DB missing: {args.db}")
        sys.exit(2)
    ver = get_user_version(args.db)
    print(f"[guard] user_version={ver}, expect={args.expect}")
    if args.strict:
        sys.exit(0 if ver == args.expect else 1)
    else:
        sys.exit(0 if ver >= args.expect else 1)

if __name__ == "__main__":
    main()
