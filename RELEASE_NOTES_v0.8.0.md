# GunSonu v0.8.0

## Özeti
- Repo hijyeni düzeltildi (.gitignore eklendi ve artefact'lar takip dışına alındı)
- DB yedekleme ve migration akışı iyileştirildi
- Installer build & smoke test komut dosyaları eklendi/güncellendi
- Test komutları (run_tests.ps1) ve PDF rapor testleri organize edildi
- Dokümantasyon: README_* dosyaları (CI, Installer, DB Migration, Tests) güncellendi

## Değişiklikler (Öne Çıkanlar)
- chore: add proper .gitignore and untrack artifacts
- build: NSIS installer ve smoke test betikleri
- db: migration komutları ve şema diyagramları
- tests: PDF ve UI test adaptörleri
- docs: README_*

## Yüklemeler (Assets)
- **GunSonu.exe** (Windows)
- **GunSonu_Windows.zip** (paket)

## Yükseltme Notları
- Mevcut veritabanı dosyalarınız (.sqlite) repoya dahil değildir; kurulu dizinde tutulmalıdır.
- Yeni kurulumdan sonra ilk açılışta “run_migrations.py”/“db_migrations.py” ile şema uyumu doğrulanmalıdır.

