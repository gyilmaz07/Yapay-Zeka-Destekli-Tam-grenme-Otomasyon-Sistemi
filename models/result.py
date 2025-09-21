from dataclasses import dataclass
from typing import Optional

@dataclass
class AnalysisResult:
    def __init__(self, soru_no, ogrenci_cevap, dogru_cevap, durum, hissiyat, 
                 tema_adi, ogrenme_ciktisi, zorluk_seviyesi, guven_endeksi, tavsiye, ogrenme_baglantisi):
        self.soru_no = soru_no
        self.ogrenci_cevap = ogrenci_cevap
        self.dogru_cevap = dogru_cevap
        self.durum = durum
        self.hissiyat = hissiyat
        self.tema_adi = tema_adi
        self.ogrenme_ciktisi = ogrenme_ciktisi
        self.zorluk_seviyesi = zorluk_seviyesi
        self.guven_endeksi = guven_endeksi
        self.tavsiye = tavsiye
        self.ogrenme_baglantisi = ogrenme_baglantisi  # ✅ Yeni alan