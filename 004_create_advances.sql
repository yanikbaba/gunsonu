-- 004_create_advances.sql  (DB v4 -> v5)
-- Creates advances table for personnel advances (MAAS mode) and bumps schema_version to 5.
-- SQLite-compatible. On PostgreSQL, use GENERATED identity and TIMESTAMPTZ.

BEGIN TRANSACTION;

CREATE TABLE IF NOT EXISTS advances (
  id             INTEGER PRIMARY KEY AUTOINCREMENT,
  personnel_id   INTEGER NOT NULL,
  amount         NUMERIC(12,2) NOT NULL CHECK (amount > 0),
  date_utc       TEXT NOT NULL,
  note           TEXT,
  created_at_utc TEXT NOT NULL,
  FOREIGN KEY (personnel_id) REFERENCES personnel(id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS ix_advances_personnel_date ON advances(personnel_id, date_utc);
CREATE INDEX IF NOT EXISTS ix_advances_date ON advances(date_utc);

UPDATE meta SET value='5' WHERE key='schema_version';

COMMIT;