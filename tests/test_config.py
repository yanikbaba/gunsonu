import json, pathlib, pytest

def test_config_min_schema():
    cfg_path = pathlib.Path("config.json")
    if not cfg_path.exists():
        pytest.skip("config.json bulunamadı")
    data = json.loads(cfg_path.read_text(encoding="utf-8"))
    # Asgari beklenen anahtarlar — proje açıklamasına göre
    for key in ("QR", "esik", "marka"):
        assert key in data, f"config.json içinde '{key}' anahtarı yok"
