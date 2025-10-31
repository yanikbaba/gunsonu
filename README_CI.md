# GunSonu CI / Test Runner

Bu paket, yerel makinede ve basit CI ajanlarında tek komutla **PyTest + PDF Smoke** çalıştırır.

## Dosyalar
- `run_tests.ps1` — Birleşik koşucu (pytest → junit.xml, pdf smoke → pdf_smoke.log, summary.txt)
- `gunsonu_ci.ps1` — Orkestratör (opsiyonel, CI ajanı gibi kullanabilirsiniz)

## Kullanım
PowerShell (Yönetici **değil**):
```powershell
cd "C:\Users\Muhasebe\Desktop\gunsonu"
powershell -ExecutionPolicy Bypass -File ".\run_tests.ps1"
```
veya:
```powershell
powershell -ExecutionPolicy Bypass -File ".\gunsonu_ci.ps1"
```

### Çıktılar
- `.\reports\junit.xml` — PyTest JUnit
- `.\reports\pdf_smoke.log` — PDF smoke test log
- `.\reports\summary.txt` — Özet (pytest exit, pdf exit, boyut, SHA256)

### Çıkış kodu
- `0` → tüm testler geçti
- `1` → pytest veya pdf smoke başarısız

> Not: `.venv` varsa otomatik kullanılır; yoksa sistem Python ile çalışır.
