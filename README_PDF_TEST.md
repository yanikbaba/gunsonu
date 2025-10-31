# GunSonu — PDF Smoke Test

Bu paket, PDF üretim altyapısının **çalıştığını hızlıca kanıtlamak** için minimal bir duman (smoke) testidir.

## İçerik
- `pdf_test.ps1` — Windows PowerShell koşucu. Ortamı hazırlar, bağımlılığı kurar, PDF üretir ve doğrular.
- `pdf_probe.py` — ReportLab ile çok sayfalı küçük bir PDF üretir ve boyut kontrolü yapar.
- `dist\gunsonu_pdf_smoke.pdf` — Çalıştırdıktan sonra oluşacak örnek PDF dosyası.

## Adımlar
1. **PowerShell'i** Yönetici olmayan bir pencerede açın.
2. Klasöre gidin:
   ```powershell
   cd "<INDIRILEN_KLASOR_YOLU>"
   ```
3. Çalıştırın:
   ```powershell
   powershell -ExecutionPolicy Bypass -File .\pdf_test.ps1
   ```
4. Başarılı ise konsolda **SHA256** göreceksiniz ve PDF otomatik açılır.

## Notlar
- Python 3.10+ ve `pip` gerekiyor. Script, `reportlab` kütüphanesini **otomatik kurar** (`--user`).  
- Minimum boyut eşiği **8 KB**: Basit PDF üretiminde boş/sorunlu dosyaları yakalamak için.
- Hata durumunda, PowerShell kırmızı hata mesajı ile durur.

## Parametreler
Gerekirse `pdf_probe.py` komut satırından manuel çağrılabilir:
```powershell
python .\pdf_probe.py --out .\dist\custom.pdf --pages 3 --min-bytes 4096
```

## Temizlik
Oluşan dosyayı silmek için:
```powershell
Remove-Item .\dist\gunsonu_pdf_smoke.pdf -Force -ErrorAction SilentlyContinue
```
