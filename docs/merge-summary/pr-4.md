Merge summary for PR #4

PR: https://github.com/yanikbaba/gunsonu/pull/4
Title: Test(config): CWD Bağımlılığını Kaldır ve Kullanılmayan Raporları Temizle
Merged by: yanikbaba
Merged at: 2026-01-12T12:02:11Z (UTC)
Merge commit: 073e60572328b089973691eea60670ad42639365
Files changed: 10
Additions: +2
Deletions: -191

Description:
Bu commit, CWD bağımlılığını düzelterek ve gereksiz `reports/` dizinini kaldırarak test altyapısını daha güvenilir hale getirir.

- CWD Bağımsızlığı: `tests/test_config.py` içindeki `config.json` yolu testin çalıştığı dizinden bağımsız hale getirildi.
- Test Güçlendirme: `pytest.skip` kaldırılarak yapılandırma dosyası bulunamadığında testin başarısız olması sağlandı.
- Kod Temizliği: `reports/` dizini kaldırıldı.

Head branch: fix/config-test-cwd-10983770482594419038 (deleted)
