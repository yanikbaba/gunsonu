import importlib, pathlib
from gunsonu_test_adapter import init_db

def test_personnel_advances_minimal(tmp_path):
    db = tmp_path / "gunsonu.sqlite"
    init_db(db)
    db_model = importlib.import_module("db_model")
    db_model.ensure_schema(str(db))

    # Insert advances
    db_model.insert_advance(str(db), person="Ali", date="2025-10-01", amount=200.0, note="")
    db_model.insert_advance(str(db), person="Veli", date="2025-10-03", amount=150.0, note="")
    db_model.insert_advance(str(db), person="Ali", date="2025-10-07", amount=50.0, note="")
    db_model.insert_advance(str(db), person="Ayse", date="2025-09-29", amount=100.0, note="")
    db_model.insert_advance(str(db), person="Veli", date="2025-10-10", amount=25.5, note="")

    rows = db_model.personnel_advances_summary(str(db))
    # Should have 3 persons
    persons = [r[0] for r in rows]
    assert set(persons) == {"Ali", "Veli", "Ayse"}

    # Totals
    d = {p: (tot, last) for p, tot, last in rows}
    assert d["Ali"][0] == 250.0  # 200 + 50
    assert d["Veli"][0] == 175.5 # 150 + 25.5
    assert d["Ayse"][0] == 100.0

    # Last dates
    assert d["Ali"][1] == "2025-10-07"
    assert d["Veli"][1] == "2025-10-10"
    assert d["Ayse"][1] == "2025-09-29"

    # Monthly total (2025-10): Ali(250) + Veli(175.5) = 425.5
    total_oct = db_model.monthly_advance_total(str(db), "2025-10")
    assert total_oct == 425.5
