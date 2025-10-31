# --- PYTHONPATH fix: proje kökünü modül arama yoluna ekle ---
import sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))
# ------------------------------------------------------------

import os, pathlib, shutil, pytest
from gunsonu_test_adapter import default_db_dir, ensure_dir, init_db

@pytest.fixture(scope="session")
def work_root(tmp_path_factory):
    p = tmp_path_factory.mktemp("gunsonu_work")
    yield p

@pytest.fixture(autouse=True)
def _chdir_work(work_root, monkeypatch):
    cwd_before = pathlib.Path.cwd()
    os.chdir(work_root)
    try:
        yield
    finally:
        os.chdir(cwd_before)

@pytest.fixture
def db_file():
    db_dir = default_db_dir()
    ensure_dir(db_dir)
    db = (pathlib.Path.cwd() / "gunsonu.sqlite")
    if db.exists():
        db.unlink()
    # Gerçek bir SQLite dosyası oluştur (0 byte değil)
    init_db(db)
    return db
