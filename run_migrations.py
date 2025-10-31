# run_migrations.py — calls db_migrations.run(db_path) correctly
import sys
import db_migrations

def main():
    db_path = "gunsonu.sqlite"
    if "--db" in sys.argv:
        try:
            db_path = sys.argv[sys.argv.index("--db") + 1]
        except Exception:
            pass
    db_migrations.run(db_path)
    print("[OK] DB migrated to version 4")

if __name__ == "__main__":
    main()
