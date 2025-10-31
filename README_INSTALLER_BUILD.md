# GunSonu — Installer Build

Bu paket, PyInstaller ile `GunSonu.exe` üretip NSIS ile `setup.exe` paketler.

## Dosyalar
- `installer.nsi` — NSIS betiği (çıktı: `.\dist\setup.exe`)
- `build_installer.ps1` — Otomatik build scripti

## Gerekli yazılımlar
- **Python 3.10+**
- **NSIS** (makensis.exe PATH'te olmalı) — https://nsis.sourceforge.io/Download

## Kullanım
PowerShell (Yönetici değil):
```powershell
cd "C:\Users\Muhasebe\Desktop\gunsonu"
# Dosyaları proje köküne kopyalayın: installer.nsi, build_installer.ps1
powershell -ExecutionPolicy Bypass -File ".\build_installer.ps1"
```

### Çıktılar
- `.\dist\GunSonu\GunSonu.exe` — PyInstaller çıktısı
- `.\dist\setup.exe` — NSIS kurulum dosyası

> Not: `installer_smoke.ps1` için `-SetupPath ".\dist\setup.exe"` bu çıktı ile uyumludur.
