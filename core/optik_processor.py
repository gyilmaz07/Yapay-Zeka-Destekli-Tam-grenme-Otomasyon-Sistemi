import os
import json
import cv2
import numpy as np
from datetime import datetime
import glob
from pathlib import Path
from typing import Dict, List, Optional
from config import settings
from utils.logger import logger

class OptikProcessor:
    def __init__(self):
        self.girdi_dizini = settings.OPTIK_CEVAPLAR_DIR
        self.cikti_dizini = settings.RAPORLAR_DIR

        self.girdi_dizini.mkdir(exist_ok=True)
        self.cikti_dizini.mkdir(exist_ok=True)

        self.soru_sayisi = settings.SORU_SAYISI
        self.secenekler = settings.SECENEKLER
        self.bos_esik = 0.1
        self.dolu_esik = 0.3
        self.baloncuk_yaricap = 12
        self.baloncuk_koordinatlari = self._baloncuk_koordinatlari_olustur()
        self.hata_ayiklama = True

        logger.info(f"Eşik değerleri: Boş={self.bos_esik}, Dolu={self.dolu_esik}")

    def _baloncuk_koordinatlari_olustur(self):
        koordinatlar = {}
        for soru in range(1, 11):
            y = 120 + (soru - 1) * 30 - 5
            koordinatlar[soru] = {}
            for i, secenek in enumerate(self.secenekler):
                x = 170 + i * 30
                koordinatlar[soru][secenek] = (x, y)
        for soru in range(11, 21):
            y = 120 + (soru - 11) * 30 - 5
            koordinatlar[soru] = {}
            for i, secenek in enumerate(self.secenekler):
                x = 500 + i * 30
                koordinatlar[soru][secenek] = (x, y)
        return koordinatlar

    def _goruntu_onisle(self, img):
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        blurred = cv2.GaussianBlur(gray, (5, 5), 0)
        _, thresh = cv2.threshold(blurred, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
        return thresh

    def optik_formu_oku(self, dosya_yolu):
        try:
            img = cv2.imread(str(dosya_yolu))
            if img is None:
                raise ValueError(f"Görüntü yüklenemedi: {dosya_yolu}")

            thresh = self._goruntu_onisle(img)

            sonuclar = {
                'dosya_adi': dosya_yolu.name,
                'okul_no': self._okul_no_oku(dosya_yolu),
                'sinif_sube': self._sinif_sube_oku(dosya_yolu),
                'cevaplar': {},
                'islem_tarihi': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                'islem_durumu': 'başarılı',
                'esik_degerler': {
                    'bos_esik': self.bos_esik,
                    'dolu_esik': self.dolu_esik
                }
            }

            for soru in range(1, self.soru_sayisi + 1):
                cevap, detaylar = self._soru_cevabi_bul(thresh, soru)
                sonuclar['cevaplar'][str(soru)] = cevap
                if self.hata_ayiklama:
                    sonuclar.setdefault('hata_ayiklama', {})
                    sonuclar['hata_ayiklama'][str(soru)] = detaylar

            sonuclar['istatistikler'] = self._istatistikleri_hesapla(sonuclar)
            return sonuclar

        except Exception as e:
            logger.error(f"Hata oluştu: {str(e)}")
            return {
                'dosya_adi': dosya_yolu.name,
                'islem_durumu': 'hata',
                'hata_mesaji': str(e)
            }

    def _soru_cevabi_bul(self, thresh_img, soru_no):
        try:
            secenek_doluluk_oranlari = {}
            detaylar = {}
            r = self.baloncuk_yaricap

            for secenek, (x, y) in self.baloncuk_koordinatlari[soru_no].items():
                y1, y2 = max(0, int(y)-r), min(thresh_img.shape[0], int(y)+r)
                x1, x2 = max(0, int(x)-r), min(thresh_img.shape[1], int(x)+r)
                roi = thresh_img[y1:y2, x1:x2]

                if roi.size > 0:
                    siyah_piksel_sayisi = np.sum(roi == 0)
                    doluluk_orani = siyah_piksel_sayisi / roi.size
                    secenek_doluluk_oranlari[secenek] = doluluk_orani
                    detaylar[secenek] = round(doluluk_orani, 3)

                    if self.hata_ayiklama:
                        cv2.imwrite(f"debug_roi_soru{soru_no}_{secenek}.png", roi)

            if secenek_doluluk_oranlari:
                en_yuksek_secenek = max(secenek_doluluk_oranlari, key=secenek_doluluk_oranlari.get)
                en_yuksek_oran = secenek_doluluk_oranlari[en_yuksek_secenek]

                if en_yuksek_oran < self.bos_esik:
                    return None, detaylar
                elif en_yuksek_oran >= self.dolu_esik:
                    return en_yuksek_secenek, detaylar
                else:
                    return "belirsiz", detaylar

            return None, detaylar

        except Exception as e:
            logger.error(f"Soru {soru_no} işlenirken hata: {str(e)}")
            return None, {}

    def _istatistikleri_hesapla(self, sonuclar):
        if sonuclar['islem_durumu'] != 'başarılı':
            return {}

        cevaplar = sonuclar['cevaplar']
        bos_cevaplar = sum(1 for cevap in cevaplar.values() if cevap is None)
        secenek_dagilimi = {secenek: 0 for secenek in self.secenekler}
        for cevap in cevaplar.values():
            if cevap in secenek_dagilimi:
                secenek_dagilimi[cevap] += 1

        return {
            'toplam_soru': self.soru_sayisi,
            'dolu_cevaplar': self.soru_sayisi - bos_cevaplar,
            'bos_cevaplar': bos_cevaplar,
            'secenek_dagilimi': secenek_dagilimi
        }

    def _okul_no_oku(self, dosya_yolu):
        try:
            return dosya_yolu.stem.split('_')[2]
        except:
            return "bilinmiyor"

    def _sinif_sube_oku(self, dosya_yolu):
        try:
            return dosya_yolu.stem.split('_')[0]
        except:
            return "bilinmiyor"

    def sonuclari_kaydet(self, sonuclar, dosya_adi=None):
        try:
            if dosya_adi is None:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                dosya_adi = f"optik_sonuclar_{timestamp}.json"

            cikti_yolu = self.cikti_dizini / dosya_adi
            with open(cikti_yolu, 'w', encoding='utf-8') as f:
                json.dump(sonuclar, f, ensure_ascii=False, indent=4)

            logger.info(f"Sonuçlar kaydedildi: {cikti_yolu}")
            return cikti_yolu

        except Exception as e:
            logger.error(f"Sonuçlar kaydedilirken hata: {str(e)}")
            return None

    def process_all_forms(self):
        """Tüm optik formları işle"""
        try:
            resim_formatlari = ["*.png", "*.jpg", "*.jpeg", "*.bmp", "*.tiff"]
            dosya_yollari = []
            for pattern in resim_formatlari:
                dosya_yollari.extend(glob.glob(str(self.girdi_dizini / pattern)))

            if not dosya_yollari:
                logger.info(f"Girdi dizininde resim dosyası bulunamadı: {self.girdi_dizini}")
                return []

            logger.info(f"{len(dosya_yollari)} dosya bulundu, işlem başlatılıyor...")

            tum_sonuclar = []
            for dosya_yolu in dosya_yollari:
                dosya_yolu = Path(dosya_yolu)
                logger.info(f"İşleniyor: {dosya_yolu.name}")
                sonuc = self.optik_formu_oku(dosya_yolu)
                tum_sonuclar.append(sonuc)

                if isinstance(sonuc, dict) and sonuc.get('islem_durumu') == 'başarılı':
                    ist = sonuc.get('istatistikler', {})
                    logger.info(f"✓ Başarılı: {ist.get('dolu_cevaplar', 0)} dolu, {ist.get('bos_cevaplar', 0)} boş")
                else:
                    hata = (sonuc or {}).get('hata_mesaji', 'Bilinmeyen hata')
                    logger.info(f"✗ Hata: {hata}")

            basarili_sayisi = len([s for s in tum_sonuclar if isinstance(s, dict) and s.get('islem_durumu') == 'başarılı'])
            logger.info(f"İşlem tamamlandı: {basarili_sayisi} başarılı")
            return tum_sonuclar
        except Exception as e:
            logger.error(f"process_all_forms sırasında beklenmeyen hata: {e}")
            return []