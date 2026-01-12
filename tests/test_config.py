import json, pathlib, pytest

def test_config_min_schema():
    cfg_path = pathlib.Path(__file__).resolve().parent.parent / "config.json"
    assert cfg_path.exists(), f"config.json repo kökünde bulunamadı: {cfg_path}"
    data = json.loads(cfg_path.read_text(encoding="utf-8"))
    # Asgari beklenen anahtarlar — proje açıklamasına göre
    for key in ("QR", "esik", "marka"):
        assert key in data, f"config.json içinde '{key}' anahtarı yok"
