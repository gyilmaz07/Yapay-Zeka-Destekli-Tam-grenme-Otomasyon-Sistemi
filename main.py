#!/usr/bin/env python3
"""
Tam Öğrenme Otomasyon Sistemi - Ana Uygulama
"""

import sys
from pathlib import Path

# Proje kök dizinini Python path'ine ekle
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

from core.data_loader import DataLoader
from core.ai_engine import AIEngine
from core.reporter import Reporter
from core.optik_processor import OptikProcessor
from core.form_generator import FormGenerator
from utils.logger import logger
from gui.main_window import MainWindow

import tkinter as tk


class TamÖgrenmeOtomasyonu:
    def __init__(self):
        self.data_loader = DataLoader()
        self.ai_engine = AIEngine()
        self.reporter = Reporter()
        self.optik_processor = OptikProcessor()
        self.form_generator = FormGenerator()

    def run_gui(self):
        """GUI arayüzünü başlat"""
        root = tk.Tk()
        root.withdraw()  # Pencereyi geçici olarak gizle
        app = MainWindow(root, self)
        root.update_idletasks()  # Tüm widget'ları oluştur
        root.deiconify()  # Pencereyi yeniden göster
        root.geometry("+100+100")  # Ana ekranın sol üstüne sabitle
        root.mainloop()

    def run_cli(self):
        """Komut satırı arayüzünü başlat"""
        logger.info("Tam Öğrenme Otomasyon Sistemi başlatılıyor...")

        # Verileri yükle
        if not self.data_loader.load_all_data():
            logger.error("Veri yükleme başarısız. Sistem durduruluyor.")
            return False

        # Tüm öğrenciler için form üret
        logger.info("Öğrenci formları oluşturuluyor...")
        form_paths = self.form_generator.generate_forms_for_all_students()
        logger.info(f"{len(form_paths)} form oluşturuldu.")

        # Optik formları işle
        logger.info("Optik formlar işleniyor...")
        results = self.optik_processor.process_all_forms()
        logger.info(f"{len(results)} optik form işlendi.")

        # Analiz ve raporlama
        logger.info("Analiz ve raporlama yapılıyor...")
        self.analyze_and_report()

        logger.info("İşlem tamamlandı!")
        return True

    def analyze_and_report(self):
        """Tüm öğrencileri analiz et ve raporla"""
        questions = self.data_loader.get_questions()
        self.ai_engine.set_questions(questions)

        success_count = 0
        for optik_file in self.data_loader.optik_dosyalar:
            try:
                logger.info(f"İşleniyor: {optik_file.name}")

                # Öğrenci verilerini yükle
                student = self.data_loader.parse_optik_file(optik_file)
                if not student:
                    logger.warning(f"{optik_file.name} işlenemedi, atlanıyor")
                    continue

                # Analiz yap
                analysis_results = self.ai_engine.analyze_student(student)

                # Rapor oluştur
                report_path = self.reporter.create_student_report(student, analysis_results)

                if report_path:
                    success_count += 1
                    logger.info(f"Rapor oluşturuldu: {report_path}")
                else:
                    logger.error(f"{student.ad_soyad} için rapor oluşturulamadı")

            except Exception as e:
                logger.error(f"{optik_file.name} işlenirken hata: {e}")

        logger.info(f"İşlem tamamlandı. {success_count}/{len(self.data_loader.optik_dosyalar)} öğrenci başarıyla işlendi.")


def main():
    """Ana fonksiyon"""
    app = TamÖgrenmeOtomasyonu()

    # CLI modunda çalıştır
    if len(sys.argv) > 1 and sys.argv[1] == "-cli":
        success = app.run_cli()
        if not success:
            sys.exit(1)
    else:
        app.run_gui()


if __name__ == "__main__":
    main()
