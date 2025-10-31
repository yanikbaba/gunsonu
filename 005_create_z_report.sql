-- 005_create_z_report.sql (DB v5 -> v6)
BEGIN TRANSACTION;

CREATE TABLE IF NOT EXISTS z_report (
  id             INTEGER PRIMARY KEY AUTOINCREMENT,
  branch         TEXT,                -- optional; NULL = default branch
  date_utc       TEXT NOT NULL,       -- ISO8601 UTC
  gross          NUMERIC(12,2) NOT NULL DEFAULT 0,
  expense        NUMERIC(12,2) NOT NULL DEFAULT 0,
  net            NUMERIC(12,2) NOT NULL DEFAULT 0,
  created_at_utc TEXT NOT NULL
);

CREATE INDEX IF NOT EXISTS ix_z_report_date ON z_report(date_utc);
CREATE INDEX IF NOT EXISTS ix_z_report_branch_date ON z_report(branch, date_utc);

UPDATE meta SET value='6' WHERE key='schema_version';

COMMIT;