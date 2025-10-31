# Test CRUD for incomes/expenses/advances + monthly_totals
# Uses adapter's init_db to get a REAL sqlite file.

import pathlib
import importlib
from gunsonu_test_adapter import init_db

def test_crud_and_totals(tmp_path, monkeypatch):
    db = tmp_path / "gunsonu.sqlite"
    # initialize real sqlite
    init_db(db)

    # import db_model AFTER file exists (ensure_schema must be present)
    db_model = importlib.import_module("db_model")
    db_model.ensure_schema(str(db))

    # Insert sample data
    db_model.insert_income(str(db), date="2025-10-01", amount=1000.0, description="Satış", branch="Merkez")
    db_model.insert_income(str(db), date="2025-10-05", amount=500.0, description="Online", branch="Merkez")
    db_model.insert_expense(str(db), date="2025-10-03", amount=300.0, description="Elektrik", branch="Merkez")
    db_model.insert_advance(str(db), person="Ali", date="2025-10-07", amount=200.0, note="Avans")

    # Totals for 2025-10
    totals = db_model.monthly_totals(str(db), "2025-10")
    assert totals["incomes"] == 1500.0
    assert totals["expenses"] == 300.0
    assert totals["advances"] == 200.0
    assert totals["net"] == 1000.0

    # listing sanity
    inc = db_model.list_incomes(str(db), "2025-10")
    exp = db_model.list_expenses(str(db), "2025-10")
    adv = db_model.list_advances(str(db), "2025-10")
    assert len(inc) == 2 and len(exp) == 1 and len(adv) == 1
