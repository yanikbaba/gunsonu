import os, pathlib, time
from gunsonu_test_adapter import create_snapshot, recover_last_snapshot

def test_snapshot_and_recover(db_file):
    # Snapshot oluştur
    snap = create_snapshot(db_file)
    assert snap and snap.exists()
    # DB'yi boz ve geri yükle
    db_file.write_bytes(b"corrupted")
    ok = recover_last_snapshot(db_file)
    assert ok
    # Geri yükleme sonrası dosya boş olmamalı
    assert db_file.exists()
    assert db_file.stat().st_size > 0
