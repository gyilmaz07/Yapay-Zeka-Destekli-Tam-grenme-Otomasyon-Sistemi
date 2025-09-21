#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import json
import cv2
import numpy as np
from datetime import datetime
import glob

class TopluOptikOkuyucu:
    def __init__(self):
        self.girdi_dizini = "/home/gazy/Masaüstü/Proje_SON/optik/data/girdi/"
        self.cikti_dizini = "/home/gazy/Masaüstü/Proje_SON/optik/data/cikti/"
        
        # Dizinleri kontrol et ve yoksa oluştur
        os.makedirs(self.girdi_dizini, exist_ok=True)
        os.makedirs(self.cikti_dizini, exist_ok=True)
        
        # Optik form düzeni bilgileri
        self.soru_sayisi = 20
        self.secenekler = ['a', 'b', 'c', 'd', 'e']
        
        # Eşik değerleri - SON AYARLAR
        self.bos_esik = 0.30    # Yüksek boş eşik değeri
        self.dolu_esik = 0.50   # Düşük dolu eşik değeri
        
        # Baloncuk koordinatları
        self.baloncuk_koordinatlari = self._baloncuk_koordinatlari_olustur()
        
        # Hata ayıklama modu
        self.hata_ayiklama = True
        
        print(f"Eşik değerleri: Boş={self.bos_esik}, Dolu={self.dolu_esik}")
        
    def _baloncuk_koordinatlari_olustur(self):
        koordinatlar = {}
        
        # İlk sütun (1-10. sorular)
        for soru in range(1, 11):
            y = 120 + (soru-1)*30 - 5
            koordinatlar[soru] = {}
            for i, secenek in enumerate(self.secenekler):
                x = 170 + i*30
                koordinatlar[soru][secenek] = (x, y)
        
        # İkinci sütun (11-20. sorular)
        for soru in range(11, 21):
            y = 120 + (soru-11)*30 - 5
            koordinatlar[soru] = {}
            for i, secenek in enumerate(self.secenekler):
                x = 500 + i*30
                koordinatlar[soru][secenek] = (x, y)
                
        return koordinatlar
    
    def _goruntu_onisle(self, img):
        """Görüntüyü işleme için hazırla"""
        # Gri tonlamaya çevir
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        
        # Gürültüyü azalt
        blurred = cv2.GaussianBlur(gray, (5, 5), 0)
        
        # Otsu thresholding
        _, thresh = cv2.threshold(blurred, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
        
        return thresh
    
    def optik_formu_oku(self, dosya_yolu):
        """Optik formu işle ve cevapları, bilgileri çıkar"""
        try:
            # Görüntüyü yükle
            img = cv2.imread(dosya_yolu)
            if img is None:
                raise ValueError(f"Görüntü yüklenemedi: {dosya_yolu}")
            
            # Görüntüyü ön işleme
            thresh = self._goruntu_onisle(img)
            
            # Hata ayıklama için işlenmiş görüntüyü kaydet
            if self.hata_ayiklama:
                islenmis_dosya = os.path.join(self.cikti_dizini, "islenmis_" + os.path.basename(dosya_yolu))
                cv2.imwrite(islenmis_dosya, thresh)
                print(f"İşlenmiş görüntü kaydedildi: {islenmis_dosya}")
            
            # Sonuçları saklayacak sözlük
            sonuclar = {
                'dosya_adi': os.path.basename(dosya_yolu),
                'okul_no': self._okul_no_oku(img),
                'sinif_sube': self._sinif_sube_oku(img),
                'cevaplar': {},
                'islem_tarihi': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                'islem_durumu': 'başarılı',
                'esik_degerler': {
                    'bos_esik': self.bos_esik,
                    'dolu_esik': self.dolu_esik
                }
            }
            
            # Her soru için işaretlenmiş baloncuğu bul
            for soru in range(1, self.soru_sayisi + 1):
                cevap, detaylar = self._soru_cevabi_bul(thresh, soru)
                sonuclar['cevaplar'][soru] = cevap
                
                # Hata ayıklama bilgilerini ekle
                if self.hata_ayiklama:
                    sonuclar.setdefault('hata_ayiklama', {})
                    sonuclar['hata_ayiklama'][soru] = detaylar
            
            # İstatistikleri hesapla
            sonuclar['istatistikler'] = self._istatistikleri_hesapla(sonuclar)
            
            return sonuclar
            
        except Exception as e:
            print(f"Hata oluştu: {str(e)}")
            return {
                'dosya_adi': os.path.basename(dosya_yolu),
                'islem_durumu': 'hata',
                'hata_mesaji': str(e)
            }
    
    def _soru_cevabi_bul(self, thresh_img, soru_no):
        """Belirli bir soru için işaretlenmiş baloncuğu bul"""
        try:
            secenek_doluluk_oranlari = {}
            detaylar = {}
            
            for secenek, (x, y) in self.baloncuk_koordinatlari[soru_no].items():
                # Baloncuk bölgesini al (8 piksel yarıçap)
                y1, y2 = max(0, int(y)-8), min(thresh_img.shape[0], int(y)+8)
                x1, x2 = max(0, int(x)-8), min(thresh_img.shape[1], int(x)+8)
                
                roi = thresh_img[y1:y2, x1:x2]
                
                if roi.size > 0:
                    # Beyaz pikselleri say (işaretli alan)
                    beyaz_piksel_sayisi = np.sum(roi == 255)
                    toplam_piksel = roi.size
                    
                    # Doluluk oranını hesapla
                    doluluk_orani = beyaz_piksel_sayisi / toplam_piksel
                    secenek_doluluk_oranlari[secenek] = doluluk_orani
                    detaylar[secenek] = round(doluluk_orani, 3)  # Yuvarla
            
            # En yüksek doluluk oranına sahip seçeneği bul
            if secenek_doluluk_oranlari:
                en_yuksek_secenek = max(secenek_doluluk_oranlari, key=secenek_doluluk_oranlari.get)
                en_yuksek_oran = secenek_doluluk_oranlari[en_yuksek_secenek]
                
                # DEBUG: Her sorunun doluluk oranlarını yazdır
                print(f"Soru {soru_no}: {detaylar}, En yüksek: {en_yuksek_secenek}={en_yuksek_oran:.3f}")
                
                # Eşik değerlerini kontrol et
                if en_yuksek_oran < self.bos_esik:
                    return None, detaylar  # Boş
                elif en_yuksek_oran >= self.dolu_esik:
                    # SADECE en yüksek orana bak, çoklu işaretleme kontrolü YOK
                    return en_yuksek_secenek, detaylar  # Dolu
                else:
                    return None, detaylar  # Belirsiz (boş kabul et)
            
            return None, detaylar
                
        except Exception as e:
            print(f"Soru {soru_no} işlenirken hata: {str(e)}")
            return None, {}
    
    def _istatistikleri_hesapla(self, sonuclar):
        """Cevaplar için istatistikleri hesapla"""
        if sonuclar['islem_durumu'] != 'başarılı':
            return {}
        
        cevaplar = sonuclar['cevaplar']
        
        # Boş cevapları say
        bos_cevaplar = sum(1 for cevap in cevaplar.values() if cevap is None)
        
        # Seçenek dağılımını hesapla
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
    
    def _okul_no_oku(self, img):
        """Okul numarasını okumak için basit bir yöntem"""
        return "123456"
    
    def _sinif_sube_oku(self, img):
        """Sınıf/şube bilgisini okumak için basit bir yöntem"""
        return "10/A"
    
    def sonuclari_kaydet(self, sonuclar, dosya_adi=None):
        """Sonuçları JSON formatında kaydet"""
        try:
            if dosya_adi is None:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                dosya_adi = f"optik_sonuclar_{timestamp}.json"
            
            cikti_yolu = os.path.join(self.cikti_dizini, dosya_adi)
            
            with open(cikti_yolu, 'w', encoding='utf-8') as f:
                json.dump(sonuclar, f, ensure_ascii=False, indent=4)
            
            print(f"Sonuçlar kaydedildi: {cikti_yolu}")
            return cikti_yolu
            
        except Exception as e:
            print(f"Sonuçlar kaydedilirken hata: {str(e)}")
            return None
    
    def toplu_islem_yap(self):
        """Girdi dizinindeki tüm optik formları işle"""
        resim_formatlari = ['*.png', '*.jpg', '*.jpeg', '*.bmp', '*.tiff']
        dosya_yollari = []
        
        for format in resim_formatlari:
            dosya_yollari.extend(glob.glob(os.path.join(self.girdi_dizini, format)))
        
        if not dosya_yollari:
            print(f"Girdi dizininde resim dosyası bulunamadı: {self.girdi_dizini}")
            return None
        
        print(f"{len(dosya_yollari)} dosya bulundu, işlem başlatılıyor...")
        
        tum_sonuclar = {
            'islem_tarihi': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            'toplam_dosya': len(dosya_yollari),
            'basarili_islem': 0,
            'hatali_islem': 0,
            'sonuclar': []
        }
        
        for dosya_yolu in dosya_yollari:
            print(f"\nİşleniyor: {os.path.basename(dosya_yolu)}")
            sonuc = self.optik_formu_oku(dosya_yolu)
            
            if sonuc['islem_durumu'] == 'başarılı':
                tum_sonuclar['basarili_islem'] += 1
                istatistik = sonuc['istatistikler']
                print(f"  ✓ Başarılı: {istatistik['dolu_cevaplar']} dolu, {istatistik['bos_cevaplar']} boş")
                
                # İlk birkaç cevabı göster
                cevaplar = sonuc['cevaplar']
                ilk_cevaplar = {k: cevaplar[k] for k in list(cevaplar.keys())[:5]}
                print(f"  İlk cevaplar: {ilk_cevaplar}")
            else:
                tum_sonuclar['hatali_islem'] += 1
                print(f"  ✗ Hata: {sonuc['hata_mesaji']}")
            
            tum_sonuclar['sonuclar'].append(sonuc)
        
        self.sonuclari_kaydet(tum_sonuclar, "toplu_optik_sonuclar.json")
        
        for sonuc in tum_sonuclar['sonuclar']:
            if sonuc['islem_durumu'] == 'başarılı':
                dosya_adi = f"sonuc_{os.path.splitext(sonuc['dosya_adi'])[0]}.json"
                self.sonuclari_kaydet(sonuc, dosya_adi)
        
        print(f"\nİşlem tamamlandı: {tum_sonuclar['basarili_islem']} başarılı, {tum_sonuclar['hatali_islem']} hatalı")
        
        return tum_sonuclar

def main():
    okuyucu = TopluOptikOkuyucu()
    
    print("Girdi dizinindeki tüm optik formlar işleniyor...")
    sonuclar = okuyucu.toplu_islem_yap()
    
    if sonuclar:
        print(f"\nÖzet:")
        print(f"Toplam dosya: {sonuclar['toplam_dosya']}")
        print(f"Başarılı işlem: {sonuclar['basarili_islem']}")
        print(f"Hatalı işlem: {sonuclar['hatali_islem']}")
        
        if sonuclar['basarili_islem'] > 0:
            toplam_soru = sonuclar['sonuclar'][0]['istatistikler']['toplam_soru']
            toplam_dolu = sum(s['istatistikler']['dolu_cevaplar'] for s in sonuclar['sonuclar'] if s['islem_durumu'] == 'başarılı')
            toplam_bos = sum(s['istatistikler']['bos_cevaplar'] for s in sonuclar['sonuclar'] if s['islem_durumu'] == 'başarılı')
            
            print(f"\nOrtalama dolu cevap: {toplam_dolu / sonuclar['basarili_islem']:.1f} / {toplam_soru}")
            print(f"Ortalama boş cevap: {toplam_bos / sonuclar['basarili_islem']:.1f} / {toplam_soru}")

if __name__ == "__main__":
    main()