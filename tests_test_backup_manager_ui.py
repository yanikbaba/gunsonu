import pathlib, sqlite3, os
import backup_manager as bm

def _make_db(tmp_path):
    db = tmp_path / "gunsonu.sqlite"
    sqlite3.connect(db).close()
    return db

def test_backup_manager_lifecycle(tmp_path):
    db = _make_db(tmp_path)

    # initially empty
    rows = bm.list_snapshots(db)
    assert rows == []

    # create two snapshots
    s1 = bm.create_snapshot(db)
    assert s1.exists()
    s2 = bm.create_snapshot(db)
    assert s2.exists()

    # list should show two entries, newest first
    rows = bm.list_snapshots(db)
    assert len(rows) == 2
    names = [r[0] for r in rows]
    assert names[0] > names[1]  # timestamp-desc

    # delete the older one
    assert bm.delete_snapshot(db, names[1])
    rows2 = bm.list_snapshots(db)
    assert len(rows2) == 1

    # recover latest should succeed
    assert bm.recover_snapshot(db, None) is True