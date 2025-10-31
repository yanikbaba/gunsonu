import pytest
from decimal import Decimal
from datetime import datetime, timezone, timedelta
import sqlite3
from dataclasses import dataclass

def bootstrap_schema(db_path: str):
    with sqlite3.connect(db_path) as dbx:
        dbx.execute("CREATE TABLE IF NOT EXISTS meta (key TEXT PRIMARY KEY, value TEXT)")
        dbx.execute("INSERT OR REPLACE INTO meta(key,value) VALUES ('schema_version','5')")
        dbx.execute("CREATE TABLE IF NOT EXISTS personnel (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT)")
        dbx.execute("INSERT INTO personnel(name) VALUES ('Test Person')")
        dbx.execute("""
            CREATE TABLE IF NOT EXISTS advances (
              id INTEGER PRIMARY KEY AUTOINCREMENT,
              personnel_id INTEGER NOT NULL,
              amount NUMERIC(12,2) NOT NULL CHECK (amount > 0),
              date_utc TEXT NOT NULL,
              note TEXT,
              created_at_utc TEXT NOT NULL
            )
        """)
        dbx.commit()

@dataclass(frozen=True)
class Advance:
    id: int
    personnel_id: int
    amount: Decimal
    date_utc: str
    note: str | None
    created_at_utc: str

class AdvanceRepo:
    def __init__(self, db_path: str):
        self.db_path = db_path
    def _db(self):
        return sqlite3.connect(self.db_path)
    def insert_advance(self, personnel_id: int, amount: Decimal, note: str | None = None, when: datetime | None = None) -> int:
        if not isinstance(personnel_id, int) or personnel_id <= 0:
            raise ValueError("personnel_id invalid")
        try:
            amt = Decimal(str(amount))
        except Exception:
            raise ValueError("amount invalid")
        if amt <= 0:
            raise ValueError("amount must be > 0")
        with self._db() as db:
            cur = db.execute("SELECT 1 FROM personnel WHERE id = ?", (personnel_id,))
            if not cur.fetchone():
                raise ValueError("personnel not found")
            now = (when or datetime.now(timezone.utc)).astimezone(timezone.utc).replace(microsecond=0).isoformat()
            cur = db.execute(
                "INSERT INTO advances (personnel_id, amount, date_utc, note, created_at_utc) VALUES (?,?,?,?,?)",
                (personnel_id, str(amt), now, note, now),
            )
            return cur.lastrowid
    def sum_advances_between(self, start_iso: str, end_iso: str) -> Decimal:
        with self._db() as db:
            cur = db.execute("SELECT COALESCE(SUM(amount),0) FROM advances WHERE date_utc >= ? AND date_utc < ?", (start_iso, end_iso))
            total = cur.fetchone()[0]
            return Decimal(str(total or "0"))

def daily_summary(kasa_gelir, giderler, advances_sum):
    net_operasyonel = kasa_gelir - giderler
    net_kasa = kasa_gelir - giderler - advances_sum
    return net_operasyonel, net_kasa

@pytest.fixture
def db(tmp_path):
    dbp = tmp_path / "t.db"
    bootstrap_schema(str(dbp))
    return str(dbp)

def test_insert_advance_happy(db):
    repo = AdvanceRepo(db)
    adv_id = repo.insert_advance(1, Decimal("500"), "On odeme")
    assert isinstance(adv_id, int) and adv_id > 0

def test_insert_advance_reject_negative(db):
    repo = AdvanceRepo(db)
    with pytest.raises(ValueError):
        repo.insert_advance(1, Decimal("-1"))

def test_insert_advance_fk_fail(db):
    repo = AdvanceRepo(db)
    with pytest.raises(ValueError):
        repo.insert_advance(999, Decimal("100"))

def test_daily_summary_cash_vs_pnl(db):
    repo = AdvanceRepo(db)
    now = datetime.now(timezone.utc)
    repo.insert_advance(1, Decimal("200"), "Deneme", when=now)
    start = now.replace(hour=0, minute=0, second=0, microsecond=0)
    end = start + timedelta(days=1)
    adv_sum = repo.sum_advances_between(start.isoformat(), end.isoformat())
    net_operasyonel, net_kasa = daily_summary(Decimal("1000"), Decimal("300"), adv_sum)
    assert str(net_operasyonel) == str(Decimal("700"))
    assert str(net_kasa) == str(Decimal("500"))
