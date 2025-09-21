import tkinter as tk
from tkinter import ttk, messagebox
import threading
import os
import shutil
from pathlib import Path
from core.data_loader import DataLoader
from core.ai_engine import AIEngine
from core.reporter import Reporter
from core.optik_processor import OptikProcessor
from core.form_generator import FormGenerator
from utils.logger import logger
from gui.data_manager import DataManagerWindow
from config import settings
from utils.print_utils import print_all_svgs_in_dir
from entegre.src.optik_form_okuyucu import TopluOptikOkuyucu

class MainWindow:
    def __init__(self, root, otomasyon_app):
        self.root = root
        self.app = otomasyon_app
        self.root.title("Tam Öğrenme Otomasyon Sistemi")
        self.root.geometry("900x600")
        self.root.configure(padx=20, pady=20)
        self.setup_ui()
        self.setup_menu()

    def setup_menu(self):
        """Modern menü yapısını oluştur"""
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)

        # Dosya menüsü
        dosya_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Dosya", menu=dosya_menu)
        dosya_menu.add_command(label="Yazdır", command=self.print_all_forms)
        dosya_menu.add_separator()
        dosya_menu.add_command(label="Çıkış", command=self.root.quit)

        # Veri menüsü
        veri_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Veri", menu=veri_menu)
        veri_menu.add_command(label="Öğrenci Verileri", command=self.open_ogrenci_manager)
        veri_menu.add_command(label="Hissiyat Verileri", command=self.open_hissiyat_manager)
        veri_menu.add_command(label="Kaynak Verileri", command=self.open_kaynak_manager)
        veri_menu.add_separator()
        veri_menu.add_command(label="Tüm Verileri Yenile", command=self.refresh_all_data)
        veri_menu.add_command(label="Öğrenci Hissiyatları", command=self.open_hissiyat_editor)

        # İşlem menüsü
        islem_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="İşlem", menu=islem_menu)
        islem_menu.add_command(label="Optik Değerlendir", command=self.run_optik_degerlendir)
        islem_menu.add_command(label="Öğrenci Formları Oluştur", command=self.generate_forms)
        islem_menu.add_command(label="Optik Formları İşle", command=self.process_forms)
        islem_menu.add_command(label="Analiz ve Raporla", command=self.analyze_and_report)
        islem_menu.add_command(label="Tüm İşlemleri Çalıştır", command=self.run_all)

        # YENİ: Raporlar menüsü
        raporlar_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Raporlar", menu=raporlar_menu)
        raporlar_menu.add_command(label="Raporları İzle", command=self.open_report_viewer)

        # Yardım menüsü
        yardim_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Yardım", menu=yardim_menu)
        yardim_menu.add_command(label="Hakkında", command=self.show_about)

    def setup_ui(self):
        """Modern arayüzü kur"""
        # Ana başlık
        title_frame = ttk.Frame(self.root)
        title_frame.pack(pady=(0, 20))

        title_label = ttk.Label(
            title_frame, 
            text="Tam Öğrenme Otomasyon Sistemi",
            font=("Arial", 18, "bold"),
            foreground="#2c3e50"
        )
        title_label.pack()

        # Buton çerçevesi
        button_frame = ttk.LabelFrame(self.root, text="İşlemler", padding="15")
        button_frame.pack(pady=(0, 20), fill="x")

        # Modern butonlar
        buttons = [
            ("📝 Öğrenci Formları Oluştur", self.generate_forms),
            ("🔍 Optik Formları İşle", self.process_forms),
            ("📊 Analiz ve Raporla", self.analyze_and_report),
            ("🚀 Tüm İşlemleri Çalıştır", self.run_all),
        ]

        for text, command in buttons:
            btn = ttk.Button(
                button_frame, 
                text=text, 
                command=command,
                width=25,
                style="Accent.TButton"
            )
            btn.pack(pady=5)

        # Durum çerçevesi
        status_frame = ttk.Frame(self.root)
        status_frame.pack(fill="x", pady=(0, 10))

        ttk.Label(status_frame, text="Durum:", font=("Arial", 10, "bold")).pack(side="left")
        self.status_var = tk.StringVar(value="Hazır")
        status_label = ttk.Label(status_frame, textvariable=self.status_var, font=("Arial", 10), foreground="#2c3e50")
        status_label.pack(side="left", padx=10)

        # Log çerçevesi
        log_frame = ttk.LabelFrame(self.root, text="İşlem Logları", padding="10")
        log_frame.pack(fill="both", expand=True, pady=(0, 10))

        # Log text alanı
        self.log_text = tk.Text(log_frame, height=15, width=80, font=("Consolas", 9), wrap="word")

        # Scrollbar
        scrollbar = ttk.Scrollbar(log_frame, orient="vertical", command=self.log_text.yview)
        self.log_text.configure(yscrollcommand=scrollbar.set)

        self.log_text.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Stil ayarları
        self.configure_styles()

    def configure_styles(self):
        """Modern stil ayarları"""
        style = ttk.Style()
        style.configure("Accent.TButton", font=("Arial", 10, "bold"), padding=(10, 5))
        style.configure("TLabelFrame", font=("Arial", 11, "bold"))
        style.configure("TLabelFrame.Label", font=("Arial", 11, "bold"))

    def show_about(self):
        """Hakkında penceresi"""
        about_text = """Tam Öğrenme Otomasyon Sistemi
Versiyon: 1.0
Geliştirici: [Your Name]
Tarih: 2025

Öğrenci takip ve değerlendirme otomasyon sistemi."""
        messagebox.showinfo("Hakkında", about_text)

    def print_all_forms(self):
        """template_output altındaki tüm SVG formlarını yazdır."""
        try:
            svg_dir = settings.TEMPLATE_OUTPUT_DIR.resolve()
            if not messagebox.askyesno(
                "Yazdır", 
                f"{svg_dir}\nklasöründeki tüm SVG formlar yazıcıya gönderilsin mi?"
            ):
                return

            self.set_status("Yazdırma başlatıldı ...")
            self.log(f"Yazdırma: {svg_dir}")

            def run_print():
                try:
                    count = print_all_svgs_in_dir(svg_dir, printer=None, copies=1)
                    if count == 0:
                        self.set_status("Yazdırılacak dosya bulunamadı veya yazdırma başarısız")
                        self.log("Not: Yazdırma kuyruğuna dosya gönderilemedi.")
                    else:
                        self.set_status(f"Yazdırma tamamlandı: {count} dosya gönderildi")
                        self.log(f"Yazdırma tamamlandı: {count} SVG yazıcıya gönderildi")
                except Exception as e:
                    self.set_status("Yazdırma hatası")
                    self.log(f"Yazdırma hatası: {e}")
                    logger.error(f"Yazdırma hatası: {e}")
                    try:
                        messagebox.showerror("Hata", f"Yazdırma hatası: {e}")
                    except Exception:
                        pass

            threading.Thread(target=run_print, daemon=True).start()
        except Exception as e:
            self.set_status("Yazdırma hatası")
            self.log(f"Yazdırma hatası: {e}")
            logger.error(f"Yazdırma hatası: {e}")
            try:
                messagebox.showerror("Hata", f"Yazdırma hatası: {e}")
            except Exception:
                pass

    def run_optik_degerlendir(self):
        """Optik formları girdi dizininden okuyup çıktı üretir"""
        girdi = "/home/gazy/Masaüstü/Tam_Ogrenme_Otomasyonu/data/optik_degerlendir/girdi/"
        cikti = "/home/gazy/Masaüstü/Tam_Ogrenme_Otomasyonu/data/optik_degerlendir/cikti/"
        hedef = "/home/gazy/Masaüstü/Tam_Ogrenme_Otomasyonu/data/optik_cevaplar/"  # Yeni hedef yol

        self.set_status("Optik değerlendirme başlatılıyor...")
        self.log(f"Girdi: {girdi}\nÇıktı: {cikti}\nHedef: {hedef}")

        def run_processing():
            try:
                os.makedirs(girdi, exist_ok=True)
                os.makedirs(cikti, exist_ok=True)
                os.makedirs(hedef, exist_ok=True)

                okuyucu = TopluOptikOkuyucu()
                okuyucu.girdi_dizini = girdi
                okuyucu.cikti_dizini = cikti
                sonuclar = okuyucu.toplu_islem_yap()

                if sonuclar:
                    self._transfer_files_to_optik_cevaplar(cikti, hedef)
                    self.set_status("Optik değerlendirme tamamlandı")
                    self.log(f"Başarılı: {sonuclar['basarili_islem']}, Hatalı: {sonuclar['hatali_islem']}")
                    messagebox.showinfo(
                        "Tamamlandı", 
                        f"Optik değerlendirme tamamlandı.\nBaşarılı: {sonuclar['basarili_islem']}, Hatalı: {sonuclar['hatali_islem']}"
                    )
                else:
                    self.set_status("Hiç dosya bulunamadı")
                    self.log("Girdi klasöründe işlenecek dosya bulunamadı.")
                    messagebox.showwarning("Uyarı", "Girdi klasöründe işlenecek dosya bulunamadı.")
            except Exception as e:
                self.set_status("Optik değerlendirme hatası")
                self.log(f"Hata: {e}")
                messagebox.showerror("Hata", f"Optik değerlendirme sırasında hata: {e}")

        threading.Thread(target=run_processing, daemon=True).start()

    def _transfer_files_to_optik_cevaplar(self, kaynak_dizin, hedef_dizin):
        """Çıktı dosyalarını optik_cevaplar dizinine taşır/kopyalar"""
        try:
            json_dosyalari = [f for f in os.listdir(kaynak_dizin) if f.endswith('.json')]
            for dosya in json_dosyalari:
                kaynak_yol = os.path.join(kaynak_dizin, dosya)
                hedef_yol = os.path.join(hedef_dizin, dosya)
                shutil.copy2(kaynak_yol, hedef_yol)
                self.log(f"Dosya kopyalandı: {dosya} → {hedef_dizin}")

            self.log(f"{len(json_dosyalari)} dosya optik_cevaplar dizinine kopyalandı")
        except Exception as e:
            self.log(f"Dosya transfer hatası: {e}")
            logger.error(f"Dosya transfer hatası: {e}")

    def open_hissiyat_editor(self):
        from gui.hissiyat_window_tk import HissiyatWindowTk
        HissiyatWindowTk()

    def open_ogrenci_manager(self):
        DataManagerWindow(self.root, "Öğrenci Veri Yöneticisi", "ogrenci")

    def open_hissiyat_manager(self):
        DataManagerWindow(self.root, "Hissiyat Veri Yöneticisi", "hissiyatlar")

    def open_kaynak_manager(self):
        DataManagerWindow(self.root, "Kaynak Veri Yöneticisi", "kaynaklar")

    def open_report_viewer(self):
        """Rapor görüntüleyiciyi aç"""
        try:
            from gui.report_viewer import ReportViewer
            ReportViewer(self.root)
            self.log("Rapor görüntüleyici açıldı")
        except ImportError as e:
            self.log(f"Rapor görüntüleyici açılamadı: {e}")
            messagebox.showerror("Hata", f"Rapor görüntüleyici modülü bulunamadı: {e}")
        except Exception as e:
            self.log(f"Rapor görüntüleyici hatası: {e}")
            messagebox.showerror("Hata", f"Rapor görüntüleyici açılırken hata: {e}")

    def refresh_all_data(self):
        self.log("Tüm veriler yeniden yükleniyor...")
        success = self.app.data_loader.load_all_data()
        if success:
            self.log("Veriler başarıyla yeniden yüklendi")
        else:
            self.log("Veri yükleme hatası!")

    def generate_forms(self):
        self.set_status("Formlar oluşturuluyor...")
        self.log("Öğrenci formları oluşturulmaya başlandı")

        def run_generation():
            try:
                form_paths = self.app.form_generator.generate_forms_for_all_students()
                if not isinstance(form_paths, list):
                    self.log("Uyarı: Form oluşturma çıktısı beklenmedik formatta. Boş liste kabul ediliyor.")
                    form_paths = []

                self.set_status(f"{len(form_paths)} form oluşturuldu")
                self.log(f"Form oluşturma tamamlandı: {len(form_paths)} dosya")
            except Exception as e:
                self.set_status("Form oluşturma hatası")
                self.log(f"Hata: {str(e)}")
                logger.error(f"Form oluşturma hatası: {e}")
                try:
                    messagebox.showerror("Hata", f"Form oluşturma hatası: {e}")
                except Exception:
                    pass

        threading.Thread(target=run_generation, daemon=True).start()

    def process_forms(self):
        self.set_status("Optik formlar işleniyor...")
        self.log("Optik formlar işlenmeye başlandı")

        def run_processing():
            try:
                results = self.app.optik_processor.process_all_forms()
                if not isinstance(results, list):
                    self.log("Uyarı: Optik işlem sonuçları beklenmedik formatta. Boş liste kabul ediliyor.")
                    results = []

                success_count = len([r for r in results if isinstance(r, dict) and r.get('islem_durumu') == 'başarılı'])
                self.set_status(f"{success_count}/{len(results)} form işlendi")
                self.log(f"Optik işleme tamamlandı: {success_count} başarılı")
                
                if len(results) == 0:
                    self.log("Not: İşlenecek resim bulunamadı veya sonuç üretilemedi.")
            except Exception as e:
                self.set_status("Optik işleme hatası")
                self.log(f"Hata: {str(e)}")
                logger.error(f"Optik işleme hatası: {e}")
                try:
                    messagebox.showerror("Hata", f"Optik işleme hatası: {e}")
                except Exception:
                    pass

        threading.Thread(target=run_processing, daemon=True).start()

    def analyze_and_report(self):
        self.set_status("Analiz yapılıyor...")
        self.log("Analiz ve raporlama başladı")

        def run_analysis():
            try:
                if not self.app.data_loader.load_all_data():
                    self.set_status("Veri yükleme hatası")
                    self.log("Veriler yüklenemedi")
                    return

                if hasattr(self.app.data_loader, "get_questions"):
                    questions = self.app.data_loader.get_questions()
                else:
                    raise AttributeError("DataLoader.get_questions() bulunamadı.")

                self.app.ai_engine.set_questions(questions)
                success_count = 0

                for optik_file in self.app.data_loader.optik_dosyalar:
                    try:
                        student = self.app.data_loader.parse_optik_file(optik_file)
                        if student:
                            analysis_results = self.app.ai_engine.analyze_student(student)
                            report_path = self.app.reporter.create_student_report(student, analysis_results)
                            if report_path:
                                success_count += 1
                                self.log(f"Rapor oluşturuldu: {student.ad_soyad}")
                        else:
                            self.log(f"Atlandı: {optik_file.name} öğrenci verisi oluşturulamadı")
                    except Exception as e:
                        self.log(f"Hata: {optik_file.name} işlenirken hata: {e}")
                        logger.error(f"Analiz sırasında hata ({optik_file.name}): {e}")

                self.set_status(f"{success_count} rapor oluşturuldu")
                self.log(f"Analiz tamamlandı: {success_count} rapor")
                
                if success_count == 0:
                    self.log("Uyarı: Hiç rapor oluşturulamadı. Optik verileri ve soru yüklemeyi kontrol edin.")
            except Exception as e:
                self.set_status("Analiz hatası")
                self.log(f"Hata: {str(e)}")
                logger.error(f"Analiz hatası: {e}")
                try:
                    messagebox.showerror("Hata", f"Analiz hatası: {e}")
                except Exception:
                    pass

        threading.Thread(target=run_analysis, daemon=True).start()

    def run_all(self):
        self.log("Tüm işlemler başlatıldı")

        def run_all_processes():
            try:
                self.set_status("Formlar oluşturuluyor...")
                form_paths = self.app.form_generator.generate_forms_for_all_students()
                if not isinstance(form_paths, list):
                    self.log("Uyarı: Form oluşturma çıktısı beklenmedik formatta. Boş liste kabul ediliyor.")
                    form_paths = []
                self.log(f"Form oluşturma tamamlandı: {len(form_paths)} dosya")

                self.set_status("Optik formlar işleniyor...")
                results = self.app.optik_processor.process_all_forms()
                if not isinstance(results, list):
                    self.log("Uyarı: Optik işlem sonuçları beklenmedik formatta. Boş liste kabul ediliyor.")
                    results = []
                success_count = len([r for r in results if isinstance(r, dict) and r.get('islem_durumu') == 'başarılı'])
                self.log(f"Optik işleme tamamlandı: {success_count}/{len(results)} başarılı")

                self.set_status("Analiz yapılıyor...")
                self.analyze_and_report()

            except Exception as e:
                self.set_status("İşlem hatası")
                self.log(f"Hata: {str(e)}")
                logger.error(f"Tüm işlemler hatası: {e}")
                try:
                    messagebox.showerror("Hata", f"Tüm işlemler hatası: {e}")
                except Exception:
                    pass

        threading.Thread(target=run_all_processes, daemon=True).start()

    def set_status(self, message):
        try:
            self.status_var.set(message)
            self.root.update_idletasks()
        except Exception as e:
            logger.error(f"Durum güncellenemedi: {e}")

    def log(self, message):
        try:
            self.log_text.insert(tk.END, f"{message}\n")
            self.log_text.see(tk.END)
            self.root.update_idletasks()
        except Exception as e:
            logger.error(f"Log yazılamadı: {e}")

    def open_report_viewer(self):
        """Rapor görüntüleyici penceresini aç"""
        from gui.report_viewer import ReportViewerWindow
        ReportViewerWindow(self.root)