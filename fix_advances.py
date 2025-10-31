import sqlite3, sys
db = "gunsonu.sqlite"
con = sqlite3.connect(db)
cur = con.cursor()

# advances tablosu var mı?
cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='advances'")
if cur.fetchone():
    cols = [r[1] for r in cur.execute("PRAGMA table_info(advances)")]
    if "personnel_id" not in cols:
        # Hızlı kurtarma: NOT NULL/FK burada eklenmez; app katmanı doğruluyor.
        cur.execute("ALTER TABLE advances ADD COLUMN personnel_id INTEGER")
        con.commit()
        print("✅ advances.personnel_id kolonu eklendi (hızlı düzeltme).")
    else:
        print("ℹ️ advances.personnel_id zaten var.")
else:
    print("ℹ️ advances tablosu yok; migration oluşturacak.")

con.close()
