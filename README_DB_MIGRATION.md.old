# GunSonu — DB Migration (Fix: `expenses` has more than one primary key)

Bu paket, `expenses` tablosundaki **çoklu PRIMARY KEY** hatasını giderir ve tabloyu güvenli şekilde **tekil PK** (`id INTEGER PRIMARY KEY AUTOINCREMENT`) ile yeniden oluşturur.

## Dosyalar
1. `migrate_expenses_pk.py` — **Otomatik göç** scripti (önerilen yol)
2. `migration_expenses_fix.sql` — Nihai şema (referans / manuel oluşturma için)
3. `db_model_expenses_fixed.py` — Uygulama tarafı **tekil PK** şeması ile örnek model
4. `README_DB_MIGRATION.md` — Bu dosya

> Not: Script, mevcut kolonları **korur ve kopyalar**. Eski tabloda `id` kolonu varsa onu da taşır; yoksa yeni tabloda **otomatik artan** `id` üretir.

---

## 1) Çalıştırma (Önerilen)

**ÖNCE YEDEK:** (Önemli)
```powershell
cd "C:\Users\Muhasebe\Desktop\gunsonu"
Copy-Item ".\gunsonu.sqlite" ".\backup\gunsonu.before_migration.sqlite" -Force
```

**Göç:**
```powershell
# Script'i proje klasörüne koyduktan sonra:
python ".\migrate_expenses_pk.py" --db ".\gunsonu.sqlite"
```

Beklenen çıktı:
```
[OK] expenses -> expenses_new -> expenses (tekil PK) taşındı.
[OK] Satır sayısı korundu: N
[OK] PRAGMA integrity_check: ok
```

---

## 2) Manuel (SQL) — gerekirse

```sql
-- Bu sadece nihai şemayı gösterir (dinamik kolon eşleme yapmaz).
CREATE TABLE IF NOT EXISTS expenses (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  date TEXT NOT NULL,
  category TEXT NOT NULL,
  description TEXT,
  amount REAL NOT NULL,
  created_at TEXT DEFAULT CURRENT_TIMESTAMP
);
```

> Eski tablodan veri taşıma işini **otomatik** yapan şey `migrate_expenses_pk.py` scriptidir. Manuel SQL ile taşıma yapmak risklidir.

---

## 3) Uygulama tarafı

- `db_model_expenses_fixed.py` içindeki `SCHEMA_SQL` kısmı tekil PK ile güncellenmiştir.
- Uygulamanın kullandığı model dosyası `db_model.py` ise, oradaki tablo tanımını **aynı** hale getiriniz.

---

## 4) Doğrulama

```powershell
# Temel doğrulamalar
python - << 'PY'
import sqlite3, sys
con = sqlite3.connect(r'.\gunsonu.sqlite')
cur = con.execute("PRAGMA table_info(expenses)")
print(list(cur))
cur = con.execute("SELECT count(*) FROM expenses")
print("rows:", cur.fetchone()[0])
print("integrity:", con.execute("PRAGMA integrity_check").fetchone()[0])
PY
```

---

## 5) Rollback (gerekirse)

```powershell
Copy-Item ".\backup\gunsonu.before_migration.sqlite" ".\gunsonu.sqlite" -Force
```

Güle güle kullan. ✅