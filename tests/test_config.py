import json, pathlib, pytest

def test_config_min_schema():
    # Testler repo kökünden farklı bir yerden çalıştırılabileceği için,
    # bu dosyanın konumuna göre config.json'a giden yolu bulalım.
    root = pathlib.Path(__file__).parent.parent
    cfg_path = root / "config.json"
    if not cfg_path.exists():
        pytest.skip(f"config.json bulunamadı aranan yer: {cfg_path}")
    data = json.loads(cfg_path.read_text(encoding="utf-8"))
    # Asgari beklenen anahtarlar — proje açıklamasına göre
    for key in ("QR", "esik", "marka"):
        assert key in data, f"config.json içinde '{key}' anahtarı yok"
