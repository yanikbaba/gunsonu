
from __future__ import annotations
import sqlite3
from decimal import Decimal
from datetime import datetime, timezone

def _connect(db: str) -> sqlite3.Connection:
    return sqlite3.connect(db)

def _iso_date(date: str) -> str:
    try:
        y, m, d = map(int, date.split("-")[:3])
        return f"{y:04d}-{m:02d}-{d:02d}"
    except Exception:
        return datetime.now(timezone.utc).strftime("%Y-%m-%d")

# ---------------- Schema ----------------
def ensure_schema(db: str) -> int:
    with _connect(db) as con:
        c = con.cursor()

        # personnel
        c.execute("CREATE TABLE IF NOT EXISTS personnel(id INTEGER PRIMARY KEY, name TEXT)")

        # advances
        c.execute("""CREATE TABLE IF NOT EXISTS advances(
            id INTEGER PRIMARY KEY,
            personnel_id INTEGER,
            amount REAL,
            date TEXT,
            note TEXT
        )""")
        # Ensure required columns exist
        adv_cols = {row[1] for row in c.execute("PRAGMA table_info(advances)")}
        if "personnel_id" not in adv_cols:
            c.execute("ALTER TABLE advances ADD COLUMN personnel_id INTEGER")
        if "amount" not in adv_cols:
            c.execute("ALTER TABLE advances ADD COLUMN amount REAL")
        if "date" not in adv_cols:
            c.execute("ALTER TABLE advances ADD COLUMN date TEXT")
        if "note" not in adv_cols:
            c.execute("ALTER TABLE advances ADD COLUMN note TEXT")

        # incomes / expenses
        c.execute("""CREATE TABLE IF NOT EXISTS incomes(
            id INTEGER PRIMARY KEY,
            date TEXT,
            amount REAL,
            description TEXT,
            branch TEXT
        )""")
        c.execute("""CREATE TABLE IF NOT EXISTS expenses(
            id INTEGER PRIMARY KEY,
            date TEXT,
            amount REAL,
            description TEXT,
            branch TEXT
        )""")

        # z_report
        c.execute("CREATE TABLE IF NOT EXISTS z_report(id INTEGER PRIMARY KEY)")
        zr_cols = {row[1] for row in c.execute("PRAGMA table_info(z_report)")}
        if "branch" not in zr_cols:
            c.execute("ALTER TABLE z_report ADD COLUMN branch TEXT")
        if "date" not in zr_cols:
            c.execute("ALTER TABLE z_report ADD COLUMN date TEXT")
        if "gross" not in zr_cols:
            c.execute("ALTER TABLE z_report ADD COLUMN gross REAL DEFAULT 0")
        if "expense" not in zr_cols:
            c.execute("ALTER TABLE z_report ADD COLUMN expense REAL DEFAULT 0")
        if "net" not in zr_cols:
            c.execute("ALTER TABLE z_report ADD COLUMN net REAL DEFAULT 0")
        if "cash_total" not in zr_cols:
            c.execute("ALTER TABLE z_report ADD COLUMN cash_total REAL DEFAULT 0")
        if "pos_total" not in zr_cols:
            c.execute("ALTER TABLE z_report ADD COLUMN pos_total REAL DEFAULT 0")
        if "qr_included" not in zr_cols:
            c.execute("ALTER TABLE z_report ADD COLUMN qr_included INTEGER DEFAULT 0")

        con.commit()
    return 8

# ---------------- Helpers ----------------
def _upsert_z(con: sqlite3.Connection, date: str, branch: str|None, d_gross: float, d_expense: float):
    """Maintain z_report and cash_total; keep pos_total=0, qr_included=0 unless you extend inputs."""
    b = branch
    cur = con.cursor()
    row = cur.execute(
        "SELECT id, gross, expense, cash_total, pos_total FROM z_report WHERE date=? AND (branch IS ? OR branch=?)",
        (date, b, b)
    ).fetchone()
    if row:
        rid, g, e, ct, pt = row
        g2 = float(g or 0) + float(d_gross)
        e2 = float(e or 0) + float(d_expense)
        n2 = g2 - e2
        ct2 = float(ct or 0) + float(d_gross) - float(d_expense)
        pt2 = float(pt or 0)  # unchanged (no POS input yet)
        cur.execute("UPDATE z_report SET gross=?, expense=?, net=?, cash_total=?, pos_total=? WHERE id=?",
                    (g2, e2, n2, ct2, pt2, rid))
    else:
        g2 = float(d_gross)
        e2 = float(d_expense)
        n2 = g2 - e2
        ct2 = g2 - e2
        pt2 = 0.0
        cur.execute(
            "INSERT INTO z_report(branch, date, gross, expense, net, cash_total, pos_total, qr_included) "
            "VALUES (?,?,?,?,?,?,?,?)",
            (b, date, g2, e2, n2, ct2, pt2, 0)
        )

# ---------------- CRUD ----------------
def insert_income(db: str, date: str, amount, description: str = "", branch: str|None = None):
    amt = float(Decimal(str(amount)))
    d = _iso_date(date)
    with _connect(db) as con:
        con.execute("INSERT INTO incomes(date,amount,description,branch) VALUES (?,?,?,?)",
                    (d, amt, description, branch))
        _upsert_z(con, d, branch, d_gross=amt, d_expense=0.0)
        con.commit()

def insert_expense(db: str, date: str, amount, description: str = "", branch: str|None = None):
    amt = float(Decimal(str(amount)))
    d = _iso_date(date)
    with _connect(db) as con:
        con.execute("INSERT INTO expenses(date,amount,description,branch) VALUES (?,?,?,?)",
                    (d, amt, description, branch))
        _upsert_z(con, d, branch, d_gross=0.0, d_expense=amt)
        con.commit()

def insert_advance(db: str, person: str, date: str, amount, note: str = ""):
    amt = float(Decimal(str(amount)))
    d = _iso_date(date)
    with _connect(db) as con:
        cur = con.cursor()
        cur.execute("SELECT id FROM personnel WHERE name=?", (person,))
        r = cur.fetchone()
        pid = r[0] if r else None
        if not pid:
            cur.execute("INSERT INTO personnel(name) VALUES(?)", (person,))
            pid = cur.lastrowid
        cur.execute("INSERT INTO advances(personnel_id,amount,date,note) VALUES (?,?,?,?)",
                    (pid, amt, d, note))
        con.commit()
        return pid

# ---------------- Queries used by tests ----------------
def monthly_totals(db: str, ym: str, branch: str|None = None):
    with _connect(db) as con:
        like = ym + "%"
        if branch:
            inc = con.execute("SELECT COALESCE(SUM(amount),0) FROM incomes WHERE date LIKE ? AND branch=?",
                              (like, branch)).fetchone()[0] or 0.0
            exp = con.execute("SELECT COALESCE(SUM(amount),0) FROM expenses WHERE date LIKE ? AND branch=?",
                              (like, branch)).fetchone()[0] or 0.0
            adv = con.execute("SELECT COALESCE(SUM(amount),0) FROM advances WHERE date LIKE ?", (like,)).fetchone()[0] or 0.0
        else:
            inc = con.execute("SELECT COALESCE(SUM(amount),0) FROM incomes WHERE date LIKE ?", (like,)).fetchone()[0] or 0.0
            exp = con.execute("SELECT COALESCE(SUM(amount),0) FROM expenses WHERE date LIKE ?", (like,)).fetchone()[0] or 0.0
            adv = con.execute("SELECT COALESCE(SUM(amount),0) FROM advances WHERE date LIKE ?", (like,)).fetchone()[0] or 0.0
    inc = float(inc); exp = float(exp); adv = float(adv)
    return {"incomes": inc, "expenses": exp, "advances": adv, "net": inc - exp - adv}

def personnel_advances_summary(db: str, ym: str|None = None):
    """Return list of (name, total_amount, last_date). last_date is YYYY-MM-DD string."""
    with _connect(db) as con:
        if ym:
            like = ym + "%"
            rows = con.execute(
                "SELECT p.name, COALESCE(SUM(a.amount),0), MAX(a.date) "
                "FROM advances a JOIN personnel p ON p.id=a.personnel_id "
                "WHERE a.date LIKE ? GROUP BY p.name ORDER BY p.name",
                (like,)
            ).fetchall()
        else:
            rows = con.execute(
                "SELECT p.name, COALESCE(SUM(a.amount),0), MAX(a.date) "
                "FROM advances a JOIN personnel p ON p.id=a.personnel_id "
                "GROUP BY p.name ORDER BY p.name"
            ).fetchall()
    return [(name, float(total or 0.0), (last or "")) for (name, total, last) in rows]

def list_incomes(db: str, ym: str|None = None, branch: str|None = None):
    with _connect(db) as con:
        q = "SELECT date, amount, description, branch FROM incomes"
        params = []
        conds = []
        if ym:
            conds.append("date LIKE ?")
            params.append(ym + "%")
        if branch:
            conds.append("branch=?")
            params.append(branch)
        if conds:
            q += " WHERE " + " AND ".join(conds)
        q += " ORDER BY date"
        return con.execute(q, tuple(params)).fetchall()

def list_expenses(db: str, ym: str|None = None, branch: str|None = None):
    with _connect(db) as con:
        q = "SELECT date, amount, description, branch FROM expenses"
        params = []
        conds = []
        if ym:
            conds.append("date LIKE ?")
            params.append(ym + "%")
        if branch:
            conds.append("branch=?")
            params.append(branch)
        if conds:
            q += " WHERE " + " AND ".join(conds)
        q += " ORDER BY date"
        return con.execute(q, tuple(params)).fetchall()

def list_advances(db: str, ym: str|None = None, branch: str|None = None):
    """Return (date, amount, person, note, branch[None]) for optional filtering by ym."""
    with _connect(db) as con:
        q = ("SELECT a.date, a.amount, p.name, a.note, NULL as branch "
             "FROM advances a JOIN personnel p ON p.id=a.personnel_id")
        params = []
        conds = []
        if ym:
            conds.append("a.date LIKE ?")
            params.append(ym + "%")
        if conds:
            q += " WHERE " + " AND ".join(conds)
        q += " ORDER BY a.date"
        return con.execute(q, tuple(params)).fetchall()
def monthly_advance_total(db: str, ym: str) -> float:
    with _connect(db) as con:
        return float(con.execute(
            "SELECT COALESCE(SUM(amount),0) FROM advances WHERE date LIKE ?",
            (ym + "%",)
        ).fetchone()[0] or 0.0)
