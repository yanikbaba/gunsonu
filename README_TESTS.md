# GunSonu Test Otomasyon Paketi (v1)

Bu paket, **GunSonu_Core_Full_v1** projesi için hızlı bir *pytest* tabanlı test otomasyonu sağlar.
Testler GUI'yi zorlamaz; çekirdek modülleri (db_model, exporter, backup_manager, crash_recovery, config.json) üzerine
odaklanır ve modül imzalarına uyum sağlamak için **dinamik adaptör** kullanır.

## Kurulum (Windows / PowerShell)
```powershell
cd "C:\Users\Muhasebe\Desktop\muhasebe genel"
# ZIP içeriğini proje köküne çıkarın; bu klasörle aynı düzeyde app.py, db_model.py vb. olmalı.

# Testleri çalıştırın:
.un_tests.ps1
```

## Ne Yapar?
1. Sanal ortam kurar ve bağımlılıkları yükler (`pytest`, `pandas`, `openpyxl`, `xlsxwriter`).
2. Dinamik adaptör ile mevcut fonksiyonları keşfeder (yoksa ilgili test **skip** edilir, fail değil).
3. Aşağıdaki kontrolleri yapar:
   - **Yol seçimi**: `D:\GunSonu\DB` varsa orası, yoksa `Belgeler\GunSonu\DB` altında çalışma dizini oluşturma.
   - **Yedekleme**: `.\.snapshots\` altında snapshot dosyası oluşumu.
   - **Dışa Aktarım**: Excel dosyası (xlsx) üretilip üretilmediği.
   - **Çökme Kurtarma**: Snapshot'tan geri dönüş akışı.
   - **config.json**: JSON şeması asgari anahtarlar.
4. Sonuçları `reports\junit.xml` olarak kaydeder; konsol özeti verir.

## Dosyalar
- `tests\conftest.py` — ortak fixture'lar ve ortam hazırlığı
- `tests\test_paths.py` — DB yolu ve çalışma alanı testi
- `tests\test_backup_and_recovery.py` — snapshot ve geri yükleme akışı
- `tests\test_exporter.py` — Excel dışa aktarma kontrolü
- `tests\test_config.py` — config.json asgari anahtarlar
- `gunsonu_test_adapter.py` — modül imzalarına uyum için dinamik çağrı katmanı
- `pytest.ini` — pytest yapılandırması
- `run_tests.ps1` — tek komutla test çalıştırıcı
- `clean_snapshots.ps1` — denemeler sonrası snapshot temizlik yardımcı scripti

## Gereksinimler
- Windows 10+ / PowerShell
- Python 3.10+ (sisteminizde kurulu olmalı)
- Proje kökünde: `app.py`, `db_model.py`, `exporter.py`, `backup_manager.py`, `crash_recovery.py`, `config.json`

> Not: Testler modül imzalarınızı **zorunlu kılmaz**. Fonksiyon bulunamazsa testler otomatik **skip** olur. Böylece adım adım entegrasyon yapabilirsiniz.
