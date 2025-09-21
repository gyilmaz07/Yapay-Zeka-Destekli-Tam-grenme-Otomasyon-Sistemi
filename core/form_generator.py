import os
import csv
from pathlib import Path
from typing import List
from config import settings
from utils.logger import logger
from utils.file_utils import load_csv_file

class FormGenerator:
    def __init__(self):
        self.output_dir = settings.TEMPLATE_OUTPUT_DIR
        self.output_dir.mkdir(exist_ok=True)
        
    def generate_forms_for_all_students(self) -> List[Path]:
        """Tüm öğrenciler için optik form oluşturur"""
        try:
            # Öğrenci verilerini yükle
            students = self._load_students()
            if not students:
                logger.warning("Öğrenci bulunamadı, demo form oluşturuluyor")
                return [self._create_demo_form()]
                
            # Her öğrenci için form oluştur
            form_paths = []
            for student in students:
                form_path = self._create_student_form(student)
                if form_path:
                    form_paths.append(form_path)
                    
            logger.info(f"{len(form_paths)} öğrenci formu oluşturuldu")
            return form_paths
            
        except Exception as e:
            logger.error(f"Form oluşturma hatası: {e}")
            return []
            
    def _load_students(self) -> List[dict]:
        """Öğrenci bilgilerini CSV'den yükler"""
        try:
            df = load_csv_file(settings.OGRENCI_PATH)
            if df.empty:
                return []
                
            students = []
            for _, row in df.iterrows():
                students.append({
                    'Ad_Soyad': row.get('Ad_Soyad', ''),
                    'Okul_No': str(row.get('Okul_No', '')),
                    'Sınıf_Sube': row.get('Sınıf_Sube', '')
                })
                
            return students
            
        except Exception as e:
            logger.error(f"Öğrenci yükleme hatası: {e}")
            return []
            
    def _create_student_form(self, student: dict) -> Path:
        """Öğrenci için optik form oluşturur"""
        try:
            ad_soyad = student['Ad_Soyad'].strip()
            okul_no = student['Okul_No'].strip()
            sinif_sube = student['Sınıf_Sube'].strip()
            
            # Dosya adı oluştur
            filename_base = f"{sinif_sube}_{okul_no}_{ad_soyad}"
            safe_filename = self._sanitize_filename(filename_base)
            output_file = self.output_dir / f"{safe_filename}.svg"
            
            # SVG içeriği oluştur
            svg_content = self._generate_svg_content(ad_soyad, okul_no, sinif_sube)
            
            # Dosyaya yaz
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(svg_content)
                
            logger.info(f"Form oluşturuldu: {output_file}")
            return output_file
            
        except Exception as e:
            logger.error(f"Öğrenci formu oluşturma hatası: {e}")
            return None
            
    def _create_demo_form(self) -> Path:
        """Demo optik form oluşturur"""
        try:
            output_file = self.output_dir / "demo_optik_form.svg"
            svg_content = self._generate_svg_content("", "", "")
            
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(svg_content)
                
            logger.info(f"Demo form oluşturuldu: {output_file}")
            return output_file
            
        except Exception as e:
            logger.error(f"Demo form oluşturma hatası: {e}")
            return None
            
    def _sanitize_filename(self, name: str) -> str:
        """Dosya adı için güvenli karakter dönüşümü"""
        import re
        name = name.strip().replace(' ', '_')
        return re.sub(r'[^\w\-_]', '_', name)
        
    def _generate_svg_content(self, ad_soyad: str, okul_no: str, sinif_sube: str) -> str:
        """SVG içeriği oluşturur"""
        svg_content = f'''<svg width="800" height="1100" xmlns="http://www.w3.org/2000/svg">
<rect width="100%" height="100%" fill="white"/>

<!-- Başlık ve bilgi alanları -->
<text x="400" y="40" text-anchor="middle" font-family="Arial, sans-serif" font-size="20" font-weight="bold">OPTİK CEVAP FORMU</text>

<!-- Öğrenci Bilgileri -->
<text x="100" y="70" text-anchor="start" font-family="Arial, sans-serif" font-size="14">Ad Soyad:</text>
<text x="180" y="70" text-anchor="start" font-family="Arial, sans-serif" font-size="14" font-weight="bold">{ad_soyad}</text>
<text x="400" y="70" text-anchor="start" font-family="Arial, sans-serif" font-size="14">Sınıf/Şube:</text>
<text x="480" y="70" text-anchor="start" font-family="Arial, sans-serif" font-size="14" font-weight="bold">{sinif_sube}</text>
<text x="600" y="70" text-anchor="start" font-family="Arial, sans-serif" font-size="14">Okul No:</text>
<text x="660" y="70" text-anchor="start" font-family="Arial, sans-serif" font-size="14" font-weight="bold">{okul_no}</text>

<!-- Seçenek başlıkları -->
<text x="120" y="100" text-anchor="middle" font-family="Arial, sans-serif" font-size="12">Soru</text>
<text x="170" y="100" text-anchor="middle" font-family="Arial, sans-serif" font-size="12">a</text>
<text x="200" y="100" text-anchor="middle" font-family="Arial, sans-serif" font-size="12">b</text>
<text x="230" y="100" text-anchor="middle" font-family="Arial, sans-serif" font-size="12">c</text>
<text x="260" y="100" text-anchor="middle" font-family="Arial, sans-serif" font-size="12">d</text>
<text x="290" y="100" text-anchor="middle" font-family="Arial, sans-serif" font-size="12">e</text>

<text x="450" y="100" text-anchor="middle" font-family="Arial, sans-serif" font-size="12">Soru</text>
<text x="500" y="100" text-anchor="middle" font-family="Arial, sans-serif" font-size="12">a</text>
<text x="530" y="100" text-anchor="middle" font-family="Arial, sans-serif" font-size="12">b</text>
<text x="560" y="100" text-anchor="middle" font-family="Arial, sans-serif" font-size="12">c</text>
<text x="590" y="100" text-anchor="middle" font-family="Arial, sans-serif" font-size="12">d</text>
<text x="620" y="100" text-anchor="middle" font-family="Arial, sans-serif" font-size="12">e</text>

<!-- Soru numaraları ve baloncuklar - İlk sütun (1-10) -->
'''

        # İlk sütun (1-10)
        for i in range(1, 11):
            y_pos = 120 + (i-1)*30
            svg_content += f'<text x="120" y="{y_pos}" text-anchor="middle" font-family="Arial, sans-serif" font-size="12">{i}</text>\n'
            
            # Baloncuklar
            for j, letter in enumerate(['a', 'b', 'c', 'd', 'e']):
                x_pos = 170 + j*30
                svg_content += f'<circle cx="{x_pos}" cy="{y_pos-5}" r="8" fill="none" stroke="black"/>\n'

        # İkinci sütun (11-20)
        for i in range(11, 21):
            y_pos = 120 + (i-11)*30
            svg_content += f'<text x="450" y="{y_pos}" text-anchor="middle" font-family="Arial, sans-serif" font-size="12">{i}</text>\n'
            
            # Baloncuklar
            for j, letter in enumerate(['a', 'b', 'c', 'd', 'e']):
                x_pos = 500 + j*30
                svg_content += f'<circle cx="{x_pos}" cy="{y_pos-5}" r="8" fill="none" stroke="black"/>\n'

        # Hizalama işaretleri
        svg_content += '''
<!-- Hizalama işaretleri -->
<circle cx="50" cy="50" r="5" fill="black"/>
<circle cx="750" cy="50" r="5" fill="black"/>
<circle cx="50" cy="1050" r="5" fill="black"/>
<circle cx="750" cy="1050" r="5" fill="black"/>

<!-- Talimatlar -->
<text x="400" y="1070" text-anchor="middle" font-family="Arial, sans-serif" font-size="10">
    Doğru cevabı işaretlemek için ilgili baloncuğu tamamen doldurunuz.
</text>
<text x="400" y="1085" text-anchor="middle" font-family="Arial, sans-serif" font-size="10">
    Birden fazla işaretleme yapmayınız ve işaretlerinizi düzgün yapınız.
</text>
</svg>'''

        return svg_content