import pandas as pd  
from pathlib import Path  
from typing import Dict, List, Tuple, Optional  
from config import settings  
from utils.file_utils import load_csv_file, load_json_file, find_optik_files  
from utils.logger import logger  
from models.student import Student  
from models.question import Question  

class DataLoader:  
    def __init__(self):
        self.kaynaklar_df = None  
        self.ogrenci_df = None  
        self.hissiyatlar_df = None  
        self.optik_dosyalar = []
        self.load_all_data()  # Otomatik veri yükleme

    def refresh_data(self):
        """Tüm verileri yeniden yükle"""
        self.load_all_data()

    def get_questions(self):
        """kaynaklar.csv içeriğini Question listesine çevirir"""
        if self.kaynaklar_df is None or self.kaynaklar_df.empty:
            return []
        questions = []
        for _, row in self.kaynaklar_df.iterrows():
            secenekler = {
                'A': str(row.get('A_Seçeneği', '')).strip(),
                'B': str(row.get('B_Seçeneği', '')).strip(),
                'C': str(row.get('C_Seçeneği', '')).strip(),
                'D': str(row.get('D_Seçeneği', '')).strip(),
                'E': str(row.get('E_Seçeneği', '')).strip(),
            }
            try:
                q = Question(
                    soru_no=int(row.get('Soru_No')),
                    soru_metni=str(row.get('Soru_Metni', '')).strip(),
                    secenekler=secenekler,
                    tema_adi=str(row.get('Tema_Adi', '')).strip(),
                    ogrenme_ciktisi=str(row.get('Ogrenme_Ciktisi', '')).strip(),
                    dogru_cevap=str(row.get('Dogru_Cevap', '')).strip(),
                    ogrenme_baglantisi=str(row.get('Ogrenme_Baglantisi', '')).strip()  # ✅ Yeni alan eklendi
                )
                questions.append(q)
            except Exception as e:
                logger.error(f"Soru satırı dönüştürme hatası: {e}")
        return questions

    def load_all_data(self) -> bool:
        """Tüm verileri yükler"""
        try:
            # Kaynakları yükle
            self.kaynaklar_df = load_csv_file(settings.KAYNAKLAR_PATH)
            if self.kaynaklar_df.empty:
                logger.error("Kaynaklar dosyası yüklenemedi")
                return False
                
            # Öğrenci bilgilerini yükle
            self.ogrenci_df = load_csv_file(settings.OGRENCI_PATH)
            if self.ogrenci_df.empty:
                logger.warning("Öğrenci dosyası yüklenemedi")
                
            # Hissiyat verilerini yükle
            self.hissiyatlar_df = load_csv_file(settings.HISSIYATLAR_PATH)
            if self.hissiyatlar_df.empty:
                logger.warning("Hissiyatlar dosyası yüklenemedi")
            else:
                self.hissiyatlar_df['Okul_No'] = self.hissiyatlar_df['Okul_No'].astype(str)
                
            # Optik dosyaları bul
            self.optik_dosyalar = find_optik_files()
            if not self.optik_dosyalar:
                logger.error("Optik dosya bulunamadı")
                return False
                
            logger.info("Tüm veriler başarıyla yüklendi")
            return True
            
        except Exception as e:
            logger.error(f"Veri yükleme hatası: {e}")
            return False

    def get_student_hissiyat(self, okul_no: str, sinif_sube: str) -> Dict[str, str]:
        """Öğrencinin hissiyat verilerini getirir"""
        if self.hissiyatlar_df is None or self.hissiyatlar_df.empty:
            return {}
            
        try:
            student_data = self.hissiyatlar_df[
                (self.hissiyatlar_df['Okul_No'] == okul_no) & 
                (self.hissiyatlar_df['Sınıf_Sube'] == sinif_sube)
            ]
            
            if student_data.empty:
                logger.warning(f"Hissiyat bulunamadı: {okul_no} - {sinif_sube}")
                return {}
                
            hissiyatlar = {}
            for i in range(1, 21):
                column_name = f'h{i}'
                if column_name in student_data.columns:
                    hissiyat_value = student_data[column_name].values[0]
                    if pd.notna(hissiyat_value):
                        hissiyatlar[str(i)] = str(hissiyat_value).strip().lower()
                    else:
                        hissiyatlar[str(i)] = "belirsiz"
                    
            logger.info(f"Hissiyat verileri yüklendi: {okul_no} - {hissiyatlar}")
            return hissiyatlar
            
        except Exception as e:
            logger.error(f"Hissiyat verisi okuma hatası: {e}")
            return {}

    def parse_optik_file(self, file_path: Path) -> Optional[Student]:
        """Optik cevap dosyasını işler ve Student nesnesi döndürür"""
        try:
            data = load_json_file(file_path)
            if not data:
                return None
                
            file_name = file_path.stem.replace('sonuc_', '')
            parts = file_name.split('_')
            
            if len(parts) < 3:
                logger.warning(f"Dosya adı formatı hatalı: {file_name}")
                return None
                
            sinif_sube = parts[0]
            okul_no = parts[1]
            ad_soyad = ' '.join(parts[2:])
            
            hissiyat_verileri = self.get_student_hissiyat(okul_no, sinif_sube)
            
            return Student(
                okul_no=okul_no,
                ad_soyad=ad_soyad,
                sinif_sube=sinif_sube,
                cevaplar=data.get('cevaplar', {}),
                hissiyat_verileri=hissiyat_verileri,
                istatistikler=data.get('istatistikler', {})
            )
            
        except Exception as e:
            logger.error(f"Optik dosya ayrıştırma hatası: {e}")
            return None