from dataclasses import dataclass
from datetime import datetime, timezone
import sqlite3
from decimal import Decimal, InvalidOperation

@dataclass(frozen=True)
class Advance:
    id: int
    personnel_id: int
    amount: Decimal
    date_utc: str
    note: str | None
    created_at_utc: str

class AdvanceRepo:
    def __init__(self, db_path: str = "gunsonu.sqlite"):
        self.db_path = db_path

    def _db(self):
        return sqlite3.connect(self.db_path)

    def insert_advance(self, personnel_id: int, amount: Decimal, note: str | None = None, when: datetime | None = None) -> int:
        if not isinstance(personnel_id, int) or personnel_id <= 0:
            raise ValueError("personnel_id invalid")

        try:
            amt = Decimal(str(amount))
        except (InvalidOperation, TypeError):
            raise ValueError("amount invalid")

        if amt <= 0:
            raise ValueError("amount must be > 0")

        with self._db() as db:
            # ensure personnel exists
            cur = db.execute("SELECT 1 FROM personnel WHERE id = ?", (personnel_id,))
            if not cur.fetchone():
                raise ValueError("personnel not found")

            now = (when or datetime.now(timezone.utc)).astimezone(timezone.utc).replace(microsecond=0)
            iso_now = now.isoformat()

            cur = db.execute(
                """
                INSERT INTO advances (personnel_id, amount, date_utc, note, created_at_utc)
                VALUES (?, ?, ?, ?, ?)
                """,
                (personnel_id, str(amt), iso_now, note, iso_now),
            )
            return cur.lastrowid

    def sum_advances_between(self, start_iso: str, end_iso: str) -> Decimal:
        with self._db() as db:
            cur = db.execute(
                """
                SELECT COALESCE(SUM(amount),0) FROM advances
                WHERE date_utc >= ? AND date_utc < ?
                """,
                (start_iso, end_iso),
            )
            total = cur.fetchone()[0]
            return Decimal(str(total or "0"))
