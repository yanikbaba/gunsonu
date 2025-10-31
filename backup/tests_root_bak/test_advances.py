# tests/test_advances.py
import pytest
from decimal import Decimal
from datetime import datetime, timezone, timedelta
import sqlite3

from app.startup import run_auto_migrations
from app.repo.advances import AdvanceRepo

# Optional: daily summary calc to verify cash vs P&L math
def daily_summary(kasa_gelir, giderler, advances_sum):
    net_operasyonel = kasa_gelir - giderler         # Avans gider değil (MAAS)
    net_kasa = kasa_gelir - giderler - advances_sum # Nakit çıkışında görünür
    return net_operasyonel, net_kasa

@pytest.fixture
def db(tmp_path):
    dbp = tmp_path / "t.db"
    run_auto_migrations(str(dbp), migrations_dir=str((tmp_path / '..' ).resolve()))  # not used; tests copy own migs if needed
    # minimal personnel seed (migration doesn't create personnel table)
    with sqlite3.connect(dbp) as dbx:
        dbx.execute("CREATE TABLE IF NOT EXISTS personnel (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT)")
        dbx.execute("INSERT INTO personnel(name) VALUES ('Test Person')")
        # Ensure meta baseline (for environments where meta doesn't exist yet)
        dbx.execute("CREATE TABLE IF NOT EXISTS meta (key TEXT PRIMARY KEY, value TEXT)")
        dbx.execute("INSERT OR REPLACE INTO meta(key,value) VALUES ('schema_version','5')")
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
    # day window (UTC)
    start = now.replace(hour=0, minute=0, second=0, microsecond=0)
    end = start + timedelta(days=1)
    adv_sum = repo.sum_advances_between(start.isoformat(), end.isoformat())
    net_operasyonel, net_kasa = daily_summary(Decimal("1000"), Decimal("300"), adv_sum)
    assert str(net_operasyonel) == str(Decimal("700"))
    assert str(net_kasa) == str(Decimal("500"))