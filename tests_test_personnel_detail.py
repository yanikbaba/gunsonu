import importlib, pathlib
from gunsonu_test_adapter import init_db
import db_model

def test_personnel_b2_summary_and_top(tmp_path):
    db = tmp_path / "gunsonu.sqlite"
    init_db(db)
    db_model.ensure_schema(str(db))

    # Seed 2025-10 advances
    db_model.insert_advance(str(db), person="Ali",  date="2025-10-01", amount=200.0, note="")
    db_model.insert_advance(str(db), person="Veli", date="2025-10-03", amount=150.0, note="")
    db_model.insert_advance(str(db), person="Ali",  date="2025-10-07", amount=50.0,  note="")
    db_model.insert_advance(str(db), person="Ayse", date="2025-09-29", amount=100.0, note="")  # out of month
    db_model.insert_advance(str(db), person="Veli", date="2025-10-10", amount=25.5, note="")

    rows = db_model.personnel_advances_summary_b2(str(db), ym="2025-10")
    d = {p: (tot, cnt, last) for p, tot, cnt, last in rows}
    assert d["Ali"]  == (250.0, 2, "2025-10-07")
    assert d["Veli"] == (175.5, 2, "2025-10-10")
    assert "Ayse" not in d  # filtered by month

    # LIKE filter
    rows_like = db_model.personnel_advances_summary_b2(str(db), person_like="ali")
    names = [r[0] for r in rows_like]
    assert "Ali" in names

    # Top list for month
    top = db_model.top_personnel_by_advance(str(db), ym="2025-10", limit=2)
    assert top[0][0] == "Ali" and top[0][1] == 250.0
    assert top[1][0] == "Veli" and top[1][1] == 175.5