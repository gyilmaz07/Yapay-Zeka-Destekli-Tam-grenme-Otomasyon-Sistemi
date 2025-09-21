import pandas as pd
from pathlib import Path
from typing import List, Dict
from config import settings
from utils.logger import logger
from models.student import Student
from models.result import AnalysisResult

class Reporter:
    def __init__(self):
        self.reports_dir = settings.RAPORLAR_DIR
        self.reports_dir.mkdir(exist_ok=True)
        
    def create_student_report(self, student: Student, analysis_results: List[AnalysisResult]) -> Path:
        """Öğrenci için detaylı rapor oluşturur"""
        try:
            # Rapor verilerini hazırla
            report_data = {
                'ogrenci_bilgileri': {
                    'okul_no': student.okul_no,
                    'ad_soyad': student.ad_soyad,
                    'sinif_sube': student.sinif_sube,
                    'tarih': pd.Timestamp.now().strftime('%d/%m/%Y %H:%M')
                },
                'analiz_sonuclari': [result.__dict__ for result in analysis_results],
                'genel_istatistikler': self._calculate_general_statistics(analysis_results)
            }
            
            # JSON raporu oluştur
            json_filename = f"rapor_{student.okul_no}_{student.ad_soyad.replace(' ', '_')}.json"
            json_path = self.reports_dir / json_filename
            from utils.file_utils import save_json_report
            save_json_report(json_path, report_data)
            
            # HTML raporu oluştur
            html_filename = f"rapor_{student.okul_no}_{student.ad_soyad.replace(' ', '_')}.html"
            html_path = self.reports_dir / html_filename
            self._create_html_report(html_path, report_data)
            
            logger.info(f"{student.ad_soyad} için rapor oluşturuldu: {html_path}")
            return html_path
            
        except Exception as e:
            logger.error(f"Rapor oluşturma hatası: {e}")
            return None
            
    def _calculate_general_statistics(self, results: List[AnalysisResult]) -> Dict:
        """Genel istatistikleri hesaplar"""
        total = len(results)
        dogru = sum(1 for r in results if r.durum == "Doğru")
        yanlis = sum(1 for r in results if r.durum == "Yanlış")
        bos = sum(1 for r in results if r.durum == "Boş")
        
        # Tema bazlı başarı oranları
        tema_basarisi = {}
        for result in results:
            tema = result.tema_adi
            if tema not in tema_basarisi:
                tema_basarisi[tema] = {'dogru': 0, 'toplam': 0}
                
            tema_basarisi[tema]['toplam'] += 1
            if result.durum == "Doğru":
                tema_basarisi[tema]['dogru'] += 1
                
        # Ortalama güven endeksi
        guven_endeksleri = [r.guven_endeksi for r in results if hasattr(r, 'guven_endeksi') and r.guven_endeksi is not None]
        ortalama_guven = sum(guven_endeksleri) / len(guven_endeksleri) if guven_endeksleri else 0
        
        return {
            'toplam_soru': total,
            'dogru_sayisi': dogru,
            'yanlis_sayisi': yanlis,
            'bos_sayisi': bos,
            'basari_orani': (dogru / total) * 100 if total > 0 else 0,
            'tema_basarisi': tema_basarisi,
            'ortalama_guven_endeksi': ortalama_guven
        }
        
    def _create_html_report(self, file_path: Path, report_data: Dict):
        """HTML raporu oluşturur"""
        html_content = f"""
        <!DOCTYPE html>
        <html lang="tr">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Tam Öğrenme Raporu - {report_data['ogrenci_bilgileri']['ad_soyad']}</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 40px; }}
                .header {{ background-color: #f8f9fa; padding: 20px; border-radius: 5px; }}
                .summary {{ margin: 20px 0; }}
                .table {{ width: 100%; border-collapse: collapse; margin: 20px 0; }}
                .table th, .table td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
                .table th {{ background-color: #f2f2f2; }}
                .correct {{ background-color: #d4edda; }}
                .wrong {{ background-color: #f8d7da; }}
                .empty {{ background-color: #fff3cd; }}
                .tema-stats {{ margin: 15px 0; }}
                .progress-bar {{ background-color: #e9ecef; border-radius: 5px; height: 20px; }}
                .progress {{ background-color: #007bff; height: 100%; border-radius: 5px; }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1>Tam Öğrenme Analiz Raporu</h1>
                <p><strong>Öğrenci:</strong> {report_data['ogrenci_bilgileri']['ad_soyad']}</p>
                <p><strong>Okul No:</strong> {report_data['ogrenci_bilgileri']['okul_no']}</p>
                <p><strong>Sınıf/Şube:</strong> {report_data['ogrenci_bilgileri']['sinif_sube']}</p>
                <p><strong>Tarih:</strong> {report_data['ogrenci_bilgileri']['tarih']}</p>
            </div>
            
            <div class="summary">
                <h2>Genel Performans Özeti</h2>
                <p><strong>Toplam Soru:</strong> {report_data['genel_istatistikler']['toplam_soru']}</p>
                <p><strong>Doğru Sayısı:</strong> {report_data['genel_istatistikler']['dogru_sayisi']}</p>
                <p><strong>Yanlış Sayısı:</strong> {report_data['genel_istatistikler']['yanlis_sayisi']}</p>
                <p><strong>Boş Sayısı:</strong> {report_data['genel_istatistikler']['bos_sayisi']}</p>
                <p><strong>Başarı Oranı:</strong> {report_data['genel_istatistikler']['basari_orani']:.2f}%</p>
                <p><strong>Ortalama Güven Endeksi:</strong> {report_data['genel_istatistikler']['ortalama_guven_endeksi']:.2f}</p>
            </div>
            
            <h2>Tema Bazlı Performans</h2>
            {"".join([self._create_tema_html(tema, stats) for tema, stats in report_data['genel_istatistikler']['tema_basarisi'].items()])}
            
            <h2>Detaylı Soru Analizi</h2>
            <table class="table">
                <thead>
                    <tr>
                        <th>Soru No</th>
                        <th>Durum</th>
                        <th>Tema</th>
                        <th>Hissiyat</th>
                        <th>Güven</th>
                        <th>Zorluk</th>
                        <th>Tavsiye</th>
                    </tr>
                </thead>
                <tbody>
                    {"".join([self._create_question_row_html(result) for result in report_data['analiz_sonuclari']])}
                </tbody>
            </table>
        </body>
        </html>
        """
        
        from utils.file_utils import save_html_report
        save_html_report(file_path, html_content)
        
    def _create_tema_html(self, tema: str, stats: Dict) -> str:
        """Tema istatistikleri için HTML oluşturur"""
        basari_orani = (stats['dogru'] / stats['toplam']) * 100 if stats['toplam'] > 0 else 0
        return f"""
        <div class="tema-stats">
            <h3>{tema}</h3>
            <p>Doğru: {stats['dogru']}/{stats['toplam']} ({basari_orani:.1f}%)</p>
            <div class="progress-bar">
                <div class="progress" style="width: {basari_orani}%"></div>
            </div>
        </div>
        """
        
    def _create_question_row_html(self, result: Dict) -> str:
        """Soru analizi için tablo satırı oluşturur"""
        row_class = ""
        if result['durum'] == "Doğru":
            row_class = "correct"
        elif result['durum'] == "Yanlış":
            row_class = "wrong"
        else:
            row_class = "empty"
            
        # Öğrenme bağlantısını kontrol et ve link olarak göster
        ogrenme_baglantisi = result.get('ogrenme_baglantisi', '')
        tavsiye = result.get('tavsiye', '')
        
        if ogrenme_baglantisi:
            tavsiye_html = f'<a href="{ogrenme_baglantisi}" target="_blank">{tavsiye}</a>'
        else:
            tavsiye_html = tavsiye
            
        return f"""
        <tr class="{row_class}">
            <td>{result['soru_no']}</td>
            <td>{result['durum']}</td>
            <td>{result['tema_adi']}</td>
            <td>{result['hissiyat']}</td>
            <td>{result.get('guven_endeksi', 0):.2f}</td>
            <td>{result.get('zorluk_seviyesi', 'Orta')}</td>
            <td>{tavsiye_html}</td>
        </tr>
        """