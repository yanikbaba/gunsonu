import importlib, pathlib

from gunsonu_test_adapter import init_db
import db_model

def test_pdf_report_minimal(tmp_path):
    db = tmp_path / "gunsonu.sqlite"
    init_db(db)
    db_model.ensure_schema(str(db))

    # seed some data
    db_model.insert_income(str(db), date="2025-10-02", amount=120.0, description="Satis", branch="Merkez")
    db_model.insert_expense(str(db), date="2025-10-03", amount=20.5, description="Gider", branch="Merkez")
    db_model.insert_advance(str(db), person="Ali", date="2025-10-05", amount=10.0, note="")

    pdf_exporter = importlib.import_module("pdf_exporter")
    out = tmp_path / "rapor.pdf"
    pdf_exporter.export_pdf(str(db), str(out), ym="2025-10")

    assert out.exists()
    data = out.read_bytes()
    # basic checks
    assert data.startswith(b"%PDF")
    assert b"2025-10" in data  # month is written in content
    assert len(data) > 200  # non-trivial file size