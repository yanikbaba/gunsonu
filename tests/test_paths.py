import pathlib
from gunsonu_test_adapter import default_db_dir, ensure_dir

def test_db_dir_selection():
    db_dir = default_db_dir()
    p = ensure_dir(db_dir)
    assert p.exists() and p.is_dir()
    # Yolun son kısmı 'GunSonu/DB' olmalı
    tail = pathlib.Path(*p.parts[-2:])
    assert str(tail).lower().replace("\\","/") == "gunsonu/db"
