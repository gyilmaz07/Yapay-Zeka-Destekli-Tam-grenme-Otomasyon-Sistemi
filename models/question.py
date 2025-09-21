from dataclasses import dataclass

@dataclass
class Question:
    def __init__(self, soru_no, soru_metni, secenekler, tema_adi, ogrenme_ciktisi, dogru_cevap, ogrenme_baglantisi):
        self.soru_no = soru_no
        self.soru_metni = soru_metni
        self.secenekler = secenekler
        self.tema_adi = tema_adi
        self.ogrenme_ciktisi = ogrenme_ciktisi
        self.dogru_cevap = dogru_cevap
        self.ogrenme_baglantisi = ogrenme_baglantisi  # ✅ Yeni alan