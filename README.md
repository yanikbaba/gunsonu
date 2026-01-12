# GunSonu Core

Bu proje, GunSonu adlı bir uygulamanın temel işlevselliğini içerir.

## Kurulum

Projeyi yerel makinenizde kurmak ve testleri çalıştırmak için aşağıdaki adımları izleyin.

1.  **Depoyu Klonlayın:**
    ```bash
    git clone <repo-adresi>
    cd <repo-dizini>
    ```

2.  **Bağımlılıkları Yükleyin:**
    Proje, `pandas` ve `pytest` gibi kütüphaneleri kullanır. Gerekli tüm bağımlılıkları yüklemek için aşağıdaki komutu çalıştırın:
    ```bash
    pip install -r requirements.txt pytest
    ```

3.  **Yapılandırma Dosyası:**
    Projenin çalışması için kök dizinde bir `config.json` dosyası bulunmalıdır. Örnek bir yapılandırma aşağıdaki gibidir:
    ```json
    {
      "QR": true,
      "esik": 100,
      "marka": "GunSonu"
    }
    ```

## Testleri Çalıştırma

Testleri çalıştırmadan önce, Python'un projenin kaynak kodunu bulabilmesi için `PYTHONPATH` ortam değişkenini ayarlamanız gerekmektedir.

Aşağıdaki komutla testleri çalıştırabilirsiniz:

```bash
export PYTHONPATH=./src && python -m pytest
```

Tüm testlerin başarıyla geçmesi gerekmektedir.
