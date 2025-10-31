#!/usr/bin/env python3
"""
Backup Consistency Probe (v0.8.1)
- Scans backup/ for *.sqlite files
- For each DB, runs lightweight integrity checks and basic counts
- Writes a human-readable report
"""
import sqlite3, glob, os, datetime, pathlib, sys

def probe_db(path):
    res = {"path": path, "ok": True, "errors": [], "counts": {}}
    try:
        con = sqlite3.connect(path)
        cur = con.execute("PRAGMA integrity_check;")
        chk = cur.fetchone()[0]
        if chk != "ok":
            res["ok"] = False
            res["errors"].append(f"integrity_check: {chk}")
        # optional tables
        for tbl in ["expenses","incomes","personnel","z_reports"]:
            try:
                c = con.execute(f"SELECT COUNT(*) FROM {tbl}").fetchone()[0]
                res["counts"][tbl] = c
            except Exception as e:
                pass
    except Exception as e:
        res["ok"] = False
        res["errors"].append(str(e))
    finally:
        try:
            con.close()
        except Exception:
            pass
    return res

def main():
    backup_dir = "backup"
    out_path = "reports/consistency_report.txt"
    pathlib.Path("reports").mkdir(parents=True, exist_ok=True)
    dbs = glob.glob(os.path.join(backup_dir, "*.sqlite"))
    lines = []
    lines.append(f"=== CONSISTENCY REPORT {datetime.datetime.now().isoformat()} ===")
    if not dbs:
        lines.append("No backup *.sqlite found.")
    for db in dbs:
        r = probe_db(db)
        state = "OK" if r["ok"] else "FAIL"
        lines.append(f"- {db}: {state}")
        if r["counts"]:
            for k,v in r["counts"].items():
                lines.append(f"    {k}: {v}")
        for e in r["errors"]:
            lines.append(f"    ! {e}")
    pathlib.Path(out_path).write_text("\n".join(lines), encoding="utf-8")
    print(f"[probe] report -> {out_path}")

if __name__ == "__main__":
    main()
