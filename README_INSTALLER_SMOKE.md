# GunSonu — Installer Smoke Test

Bu script, **setup.exe** ile kurulum → **EXE aç/kapat** → (opsiyonel) **PDF probe** → **silent uninstall** adımlarını otomatik test eder.

## Dosya
- `installer_smoke.ps1`

## Kullanım
PowerShell (Yönetici değil):
```powershell
cd "C:\Users\Muhasebe\Desktop\gunsonu"
powershell -ExecutionPolicy Bypass -File ".\installer_smoke.ps1" -SetupPath ".\dist\setup.exe" -InstallDir "C:\Program Files\GunSonu" -ProbePath ".\pdf_probe.py"
```

### Parametreler
- `-SetupPath` (**zorunlu**) — Kurulum dosyası (setup.exe) yolu
- `-InstallDir` (varsayılan: `C:\Program Files\GunSonu`) — Kurulum dizini
- `-ExeName` (varsayılan: `GunSonu.exe`) — Ana çalıştırılabilir dosya adı
- `-ProbePath` (opsiyonel) — `pdf_probe.py` yolu; verilirse kurulumdan sonra PDF smoke da çalıştırılır.
- `-LogDir` (varsayılan: `.\reports`) — Log dosyalarının konumu

### Çıkış kodu
- `0` → Başarılı
- `!=0` → Herhangi bir adımda hata

### Üretilen loglar
- `.\reports\installer_smoke.log`
- `.\reports\installer_pdf_probe.log` (Probe kullanıldıysa)

> Script, NSIS ve InnoSetup’ın yaygın sessiz kurulum/kaldırma bayraklarını (`/S`, `/silent`, `/verysilent`) dener.
