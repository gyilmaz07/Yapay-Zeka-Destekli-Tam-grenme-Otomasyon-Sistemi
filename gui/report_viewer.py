import tkinter as tk
from tkinter import ttk, messagebox, filedialog  # filedialog eklendi
import os
import webbrowser
import shutil  # shutil eklendi
from pathlib import Path
from config import settings

class ReportViewerWindow(tk.Toplevel):
    def __init__(self, master=None):
        super().__init__(master)
        self.title("Raporları İzle")
        self.geometry("800x600+100+100")
        self.reports_dir = settings.RAPORLAR_DIR
        
        self.build_ui()
        self.load_classes()
        
    def build_ui(self):
        # Ana frame
        main_frame = ttk.Frame(self, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Sınıf seçim frame
        class_frame = ttk.LabelFrame(main_frame, text="Sınıf/Şube Seçin", padding="10")
        class_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(class_frame, text="Sınıf/Şube:").pack(side=tk.LEFT, padx=5)
        self.class_var = tk.StringVar()
        self.class_combo = ttk.Combobox(class_frame, textvariable=self.class_var, width=10)
        self.class_combo.pack(side=tk.LEFT, padx=5)
        self.class_combo.bind('<<ComboboxSelected>>', self.on_class_selected)
        
        # Öğrenci listesi frame
        student_frame = ttk.LabelFrame(main_frame, text="Öğrenciler", padding="10")
        student_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        
        # Treeview için frame
        tree_frame = ttk.Frame(student_frame)
        tree_frame.pack(fill=tk.BOTH, expand=True)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(tree_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Treeview
        self.tree = ttk.Treeview(tree_frame, columns=('okul_no', 'ad_soyad', 'rapor_durumu'), 
                                yscrollcommand=scrollbar.set, selectmode='browse')
        self.tree.heading('#0', text='ID')
        self.tree.heading('okul_no', text='Okul No')
        self.tree.heading('ad_soyad', text='Ad Soyad')
        self.tree.heading('rapor_durumu', text='Rapor Durumu')
        
        self.tree.column('#0', width=0, stretch=tk.NO)
        self.tree.column('okul_no', width=80)
        self.tree.column('ad_soyad', width=200)
        self.tree.column('rapor_durumu', width=100)
        
        self.tree.pack(fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.tree.yview)
        
        # Butonlar
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=5)
        
        ttk.Button(button_frame, text="Raporu Aç", command=self.open_report).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Raporu İndir", command=self.download_report).pack(side=tk.LEFT, padx=5)  # Yeni buton
        ttk.Button(button_frame, text="Yenile", command=self.refresh).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Kapat", command=self.destroy).pack(side=tk.RIGHT, padx=5)
        
    def load_classes(self):
        """Mevcut sınıfları yükle"""
        classes = set()
        
        # Öğrenci CSV'sinden sınıfları al
        try:
            import pandas as pd
            df = pd.read_csv(settings.OGRENCI_PATH)
            if not df.empty and 'Sınıf_Sube' in df.columns:
                classes.update(df['Sınıf_Sube'].unique())
        except Exception as e:
            print(f"Sınıf yükleme hatası: {e}")
        
        # Rapor dosyalarından sınıfları al
        if self.reports_dir.exists():
            for file in self.reports_dir.glob('*.html'):
                # Dosya adı formatı: rapor_{okul_no}_{ad_soyad}.html
                parts = file.stem.split('_')
                if len(parts) >= 3:
                    # Sınıf bilgisini öğrenci CSV'sinden alacağız
                    pass
        
        self.class_combo['values'] = sorted(classes)
        
    def on_class_selected(self, event):
        """Sınıf seçildiğinde öğrencileri yükle"""
        selected_class = self.class_var.get()
        if selected_class:
            self.load_students(selected_class)
            
    def load_students(self, class_name):
        """Seçili sınıftaki öğrencileri yükle"""
        # Treeview'ı temizle
        for item in self.tree.get_children():
            self.tree.delete(item)
            
        try:
            import pandas as pd
            df = pd.read_csv(settings.OGRENCI_PATH)
            class_students = df[df['Sınıf_Sube'] == class_name]
            
            for _, student in class_students.iterrows():
                okul_no = str(student.get('Okul_No', ''))
                ad_soyad = student.get('Ad_Soyad', '')
                
                # Rapor durumunu kontrol et
                report_file = self.reports_dir / f"rapor_{okul_no}_{ad_soyad.replace(' ', '_')}.html"
                report_status = "Var" if report_file.exists() else "Yok"
                
                self.tree.insert('', 'end', values=(okul_no, ad_soyad, report_status))
                
        except Exception as e:
            messagebox.showerror("Hata", f"Öğrenci yükleme hatası: {e}")
            
    def open_report(self):
        """Seçili öğrencinin raporunu aç"""
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Uyarı", "Lütfen bir öğrenci seçin")
            return
            
        item = selected[0]
        values = self.tree.item(item, 'values')
        okul_no, ad_soyad, _ = values
        
        report_file = self.reports_dir / f"rapor_{okul_no}_{ad_soyad.replace(' ', '_')}.html"
        
        if report_file.exists():
            try:
                webbrowser.open(f'file://{report_file.resolve()}')
            except Exception as e:
                messagebox.showerror("Hata", f"Rapor açılırken hata: {e}")
        else:
            messagebox.showwarning("Uyarı", "Bu öğrenci için rapor bulunamadı")
            
    def download_report(self):
        """Seçili öğrencinin raporunu indir"""
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Uyarı", "Lütfen bir öğrenci seçin")
            return

        item = selected[0]
        values = self.tree.item(item, 'values')
        okul_no, ad_soyad, _ = values

        report_file = self.reports_dir / f"rapor_{okul_no}_{ad_soyad.replace(' ', '_')}.html"

        if not report_file.exists():
            messagebox.showwarning("Uyarı", "Bu öğrenci için rapor bulunamadı")
            return

        # Kullanıcıdan kaydetme yeri seçmesini iste
        save_path = filedialog.asksaveasfilename(
            defaultextension=".html",
            filetypes=[("HTML Files", "*.html"), ("All Files", "*.*")],
            initialfile=report_file.name
        )

        if not save_path:
            return  # Kullanıcı iptal etti

        try:
            shutil.copy2(report_file, save_path)
            messagebox.showinfo("Başarılı", f"Rapor başarıyla indirildi:\n{save_path}")
        except Exception as e:
            messagebox.showerror("Hata", f"Rapor indirilemedi:\n{e}")
            
    def refresh(self):
        """Listeyi yenile"""
        selected_class = self.class_var.get()
        if selected_class:
            self.load_students(selected_class)
        else:
            self.load_classes()