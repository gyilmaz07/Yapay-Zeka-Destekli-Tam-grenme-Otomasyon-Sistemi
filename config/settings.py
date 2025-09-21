import os
from pathlib import Path

# Temel dizin yapıları
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
SRC_DIR = BASE_DIR / "src"

# Veri dosya yolları
KAYNAKLAR_PATH = DATA_DIR / "kaynaklar" / "kaynaklar.csv"
OGRENCI_PATH = DATA_DIR / "ogrenci" / "ogrenci.csv"
OPTIK_CEVAPLAR_DIR = DATA_DIR / "optik_cevaplar"
TEMPLATE_OUTPUT_DIR = DATA_DIR / "template_output"
RAPORLAR_DIR = DATA_DIR / "raporlar"

# Optik form ayarları
SORU_SAYISI = 20
SECENEKLER = ['a', 'b', 'c', 'd', 'e']
BOS_ESIK = 0.3
DOLU_ESIK = 0.5

# AI ve Analiz ayarları
GUVEN_ESIK_DUSUK = 0.3
GUVEN_ESIK_YUKSEK = 0.7

# Loglama ayarları
LOG_DIR = BASE_DIR / "logs"
LOG_FILE = LOG_DIR / "tam_ogrenme_otomasyon.log"

# Veri dosya yolları
# Data paths
OGRENCI_PATH = DATA_DIR / "ogrenci" / "ogrenci.csv"
HISSIYATLAR_PATH = DATA_DIR / "hissiyatlar" / "hissiyatlar.csv"
KAYNAKLAR_PATH = DATA_DIR / "kaynaklar" / "kaynaklar.csv"
OPTIK_CEVAPLAR_DIR = DATA_DIR / "optik_cevaplar"

# config.py dosyasına hissiyatlar path'ini ekleyin
HISSIYATLAR_PATH = DATA_DIR / "hissiyatlar" / "hissiyatlar.csv"

# Güven eşik değerleri
GUVEN_ESIK_DUSUK = 0.3
GUVEN_ESIK_YUKSEK = 0.7

# config/settings.py

# ... mevcut ayarlarınızın altına ekleyin ...

OGRENME_BAGLANTILARI = {
    "Yapay Zeka": "https://tr.wikipedia.org/wiki/Yapay_zeka",
    "Bilgisayar Donanımı": "https://www.bilgisayarnedir.com/donanım",
    "Robotik Kodlama": "https://www.robokids.com/robotik-kodlama",
    "Bilgisayar Güvenliği": "https://www.usom.gov.tr",
    "Programlama Dilleri": "https://www.w3schools.com",
    "Dijital İletişim": "https://tr.wikipedia.org/wiki/Dijital_iletişim",
    "Bulut Bilişim": "https://azure.microsoft.com/tr-tr/resources/cloud-computing-dictionary/what-is-cloud-computing",
    "Bilgisayar Ağları": "https://tr.wikipedia.org/wiki/Bilgisayar_ağları",
    "Bilgisayar Yazılımı": "https://tr.wikipedia.org/wiki/İşletim_sistemi",
    "Dijital Okuryazarlık": "https://www.egitim.gov.tr/dijital-okuryazarlik",
    "Veri Türleri": "https://www.veribilimiokulu.com/python-veri-tipleri",
    "Algoritma": "https://tr.wikipedia.org/wiki/Algoritma",
}


