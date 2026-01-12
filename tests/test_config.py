import json, pathlib, pytest

def test_config_min_schema():
    # Testin CWD'den bağımsız olması için, test dosyasının bulunduğu dizinden yola çık
    # Repo köküne ulaşıp oradan config.json dosyasını buluyoruz.
    # __file__ -> tests/test_config.py
    # .parent -> tests/
    # .parent -> (repo kökü)
    cfg_path = pathlib.Path(__file__).resolve().parent.parent / "config.json"
    if not cfg_path.exists():
        pytest.skip(f"config.json bulunamadı: {cfg_path}")
    data = json.loads(cfg_path.read_text(encoding="utf-8"))
    # Asgari beklenen anahtarlar — proje açıklamasına göre
    for key in ("QR", "esik", "marka"):
        assert key in data, f"config.json içinde '{key}' anahtarı yok"
