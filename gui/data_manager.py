import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import pandas as pd
from pathlib import Path
from config import settings
from utils.logger import logger
from utils.file_utils import load_csv_file, save_csv_file

class DataManagerWindow:
    def __init__(self, parent, title, data_type):
        self.parent = parent
        self.data_type = data_type
        self.df = None
        self.filtered_df = None
        
        self.window = tk.Toplevel(parent)
        self.window.title(title)
        self.window.geometry("1000x600")
        self.window.transient(parent)
        self.window.grab_set()
        
        self.setup_ui()
        self.load_data()
    
    def setup_ui(self):
        """Arayüzü kur"""
        # Ana frame
        main_frame = ttk.Frame(self.window, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Buton çerçevesi
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=5)
        
        buttons = [
            ("Yeni Kayıt", self.new_record),
            ("Düzenle", self.edit_record),
            ("Sil", self.delete_record),
            ("Ara", self.search_records),
            ("Listele", self.list_all),
            ("Kaydet", self.save_data)
        ]
        
        for text, command in buttons:
            btn = ttk.Button(button_frame, text=text, command=command)
            btn.pack(side=tk.LEFT, padx=5)
        
        # Arama çerçevesi
        search_frame = ttk.Frame(main_frame)
        search_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(search_frame, text="Ara:").pack(side=tk.LEFT)
        self.search_var = tk.StringVar()
        search_entry = ttk.Entry(search_frame, textvariable=self.search_var, width=30)
        search_entry.pack(side=tk.LEFT, padx=5)
        search_entry.bind('<Return>', lambda e: self.search_records())
        
        # Treeview çerçevesi
        tree_frame = ttk.Frame(main_frame)
        tree_frame.pack(fill=tk.BOTH, expand=True)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(tree_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Treeview
        self.tree = ttk.Treeview(tree_frame, yscrollcommand=scrollbar.set, selectmode='browse')
        self.tree.pack(fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.tree.yview)
        
        # Durum çubuğu
        self.status_var = tk.StringVar(value="Hazır")
        status_bar = ttk.Label(self.window, textvariable=self.status_var, relief=tk.SUNKEN, anchor=tk.W)
        status_bar.pack(side=tk.BOTTOM, fill=tk.X)
    
    def load_data(self):
        """Verileri yükle"""
        try:
            if self.data_type == "ogrenci":
                file_path = settings.OGRENCI_PATH
            elif self.data_type == "hissiyatlar":
                file_path = settings.HISSIYATLAR_PATH
            elif self.data_type == "kaynaklar":
                file_path = settings.KAYNAKLAR_PATH
            else:
                raise ValueError("Geçersiz veri tipi!")
            
            self.df = load_csv_file(file_path)
            
            # Kaynaklar için özel işlem - Ogrenme_Baglantisi sütunu yoksa ekle
            if self.data_type == "kaynaklar" and "Ogrenme_Baglantisi" not in self.df.columns:
                self.df["Ogrenme_Baglantisi"] = ""
                
            if self.df.empty:
                messagebox.showwarning("Uyarı", f"{self.data_type} dosyası boş veya bulunamadı")
                return
                
            self.filtered_df = self.df.copy()
            self.update_treeview()
            self.status_var.set(f"{len(self.df)} kayıt yüklendi")

        except Exception as e:
            logger.error(f"Veri yükleme hatası: {e}")
            messagebox.showerror("Hata", f"Veri yüklenirken hata: {e}")
    
    def update_treeview(self):
        """Treeview'ı güncelle"""
        # Mevcut öğeleri temizle
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # Sütunları ayarla
        columns = list(self.filtered_df.columns)
        self.tree['columns'] = columns
        self.tree['show'] = 'headings'
        
        # Sütun başlıkları
        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=100, minwidth=50)
        
        # Verileri ekle
        for _, row in self.filtered_df.iterrows():
            self.tree.insert('', 'end', values=list(row))
    
    def new_record(self):
        """Yeni kayıt ekle"""
        if self.df is None or self.df.empty:
            messagebox.showwarning("Uyarı", "Önce veri yükleyin")
            return
        
        # Sütunlara göre input alanları oluştur
        dialog = RecordDialog(self.window, "Yeni Kayıt", self.df.columns.tolist())
        self.window.wait_window(dialog.top)
        
        if dialog.result:
            new_data = dialog.result
            # Yeni kaydı DataFrame'e ekle
            new_row = pd.DataFrame([new_data], columns=self.df.columns)
            self.df = pd.concat([self.df, new_row], ignore_index=True)
            self.filtered_df = self.df.copy()
            self.update_treeview()
            self.status_var.set("Yeni kayıt eklendi")
    
    def edit_record(self):
        """Kaydı düzenle"""
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Uyarı", "Düzenlenecek kaydı seçin")
            return
        
        item = selected[0]
        values = self.tree.item(item, 'values')
        index = self.tree.index(item)
        
        # Seçili kaydı düzenle
        dialog = RecordDialog(self.window, "Kaydı Düzenle", self.df.columns.tolist(), values)
        self.window.wait_window(dialog.top)
        
        if dialog.result:
            # DataFrame'i güncelle
            for i, col in enumerate(self.df.columns):
                self.df.at[index, col] = dialog.result[i]
            
            self.filtered_df = self.df.copy()
            self.update_treeview()
            self.status_var.set("Kayıt güncellendi")
    
    def delete_record(self):
        """Kaydı sil"""
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Uyarı", "Silinecek kaydı seçin")
            return
        
        if messagebox.askyesno("Onay", "Seçili kaydı silmek istediğinize emin misiniz?"):
            item = selected[0]
            index = self.tree.index(item)
            
            # DataFrame'den sil
            self.df = self.df.drop(index).reset_index(drop=True)
            self.filtered_df = self.df.copy()
            self.update_treeview()
            self.status_var.set("Kayıt silindi")
    
    def search_records(self):
        """Kayıtlarda ara"""
        if self.df is None or self.df.empty:
            messagebox.showwarning("Uyarı", "Önce veri yükleyin")
            return
        
        search_term = self.search_var.get().lower()
        if not search_term:
            self.filtered_df = self.df.copy()
        else:
            # Tüm sütunlarda ara
            mask = self.df.astype(str).apply(lambda x: x.str.lower().str.contains(search_term, na=False)).any(axis=1)
            self.filtered_df = self.df[mask]
        
        self.update_treeview()
        self.status_var.set(f"{len(self.filtered_df)} kayıt bulundu")
    
    def list_all(self):
        """Tüm kayıtları listele"""
        self.filtered_df = self.df.copy()
        self.update_treeview()
        self.status_var.set("Tüm kayıtlar listelendi")
    
    def save_data(self):
        """Verileri kaydet"""
        try:
            if self.data_type == "ogrenci":
                file_path = settings.OGRENCI_PATH
            elif self.data_type == "hissiyatlar":
                file_path = settings.HISSIYATLAR_PATH
            elif self.data_type == "kaynaklar":
                file_path = settings.KAYNAKLAR_PATH
            
            success = save_csv_file(file_path, self.df)
            if success:
                messagebox.showinfo("Başarılı", "Veriler başarıyla kaydedildi")
                self.status_var.set("Veriler kaydedildi")
            else:
                messagebox.showerror("Hata", "Veriler kaydedilemedi")
                
        except Exception as e:
            logger.error(f"Veri kaydetme hatası: {e}")
            messagebox.showerror("Hata", f"Veri kaydedilirken hata: {e}")


class RecordDialog:
    """Kayıt düzenleme/ekleme dialog penceresi"""

    def __init__(self, parent, title, columns, values=None):
        self.top = tk.Toplevel(parent)
        self.top.title(title)
        self.top.transient(parent)
        self.top.grab_set()

        self.columns = columns
        self.values = values
        self.result = None
        self.entries = {}

        self.setup_ui()

    def setup_ui(self):
        """Dialog arayüzünü kur"""
        main_frame = ttk.Frame(self.top, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Giriş alanları
        for i, col in enumerate(self.columns):
            ttk.Label(main_frame, text=f"{col}:").grid(row=i, column=0, sticky=tk.W, pady=2)
            
            # Ogrenme_Baglantisi için daha geniş bir giriş alanı
            if col == "Ogrenme_Baglantisi":
                entry = ttk.Entry(main_frame, width=50)
            else:
                entry = ttk.Entry(main_frame, width=30)
                
            entry.grid(row=i, column=1, pady=2, padx=5)

            # Varsayılan değerleri ayarla
            if self.values and i < len(self.values):
                entry.insert(0, str(self.values[i]))
                
            self.entries[col] = entry

        # Butonlar
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=len(self.columns), column=0, columnspan=2, pady=10)

        ttk.Button(button_frame, text="Kaydet", command=self.on_save).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="İptal", command=self.on_cancel).pack(side=tk.LEFT, padx=5)
    
    def on_save(self):
        """Kaydet butonu işlevi"""
        try:
            self.result = [self.entries[col].get() for col in self.columns]
            self.top.destroy()
        except Exception as e:
            messagebox.showerror("Hata", f"Kayıt işlemi sırasında hata: {e}")
    
    def on_cancel(self):
        """İptal butonu işlevi"""
        self.result = None
        self.top.destroy()