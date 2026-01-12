import pathlib, os
from gunsonu_test_adapter import export_excel, default_db_dir

def test_export_excel(db_file):
    out = export_excel(db_file, default_db_dir())
    assert out is not None, "Exporter entegrasyonu bulunamadı ve fallback başarısız oldu."
    assert out.exists(), "Excel çıktısı oluşmadı"
    assert out.suffix.lower() == ".xlsx"
    # Boyut çok küçük olmamalı (en az birkaç KB)
    assert out.stat().st_size > 1000
