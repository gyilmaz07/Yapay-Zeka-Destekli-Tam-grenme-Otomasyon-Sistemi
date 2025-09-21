import tkinter as tk
from tkinter import ttk, messagebox
import pandas as pd
from gui.scrolled_frame import ScrolledFrame

class HissiyatWindowTk(tk.Toplevel):
    def __init__(self, master=None):
        super().__init__(master)
        self.title("Öğrenci Hissiyatları")
        self.geometry("900x600+100+100")

        self.hissiyat_yolu = "./data/hissiyatlar/hissiyatlar.csv"
        self.secenekler = ["anlamadım", "çok zor", "zor", "orta", "kolay", "çok kolay"]

        try:
            self.veri = pd.read_csv(self.hissiyat_yolu)
        except Exception as e:
            messagebox.showerror("Dosya Hatası", f"Veri dosyası yüklenemedi:\n{e}")
            self.destroy()
            return

        if self.veri.empty:
            messagebox.showerror("Veri Hatası", "Hissiyatlar verisi boş.")
            self.destroy()
            return

        self.radio_varlar = {}
        self.current_index = self.veri.index[0]  # İlk öğrenci
        self.build_ui()

    def build_ui(self):
        # Arama kutusu (okul no ile)
        top = ttk.Frame(self)
        top.pack(fill="x", padx=10, pady=5)

        ttk.Label(top, text="Okul No ile Ara:").pack(side="left")
        self.search_var = tk.StringVar()
        entry = ttk.Entry(top, textvariable=self.search_var, width=20)
        entry.pack(side="left", padx=5)
        entry.bind("<Return>", lambda e: self.apply_search())
        ttk.Button(top, text="Bul", command=self.apply_search).pack(side="left", padx=5)

        # Scroll alanı
        self.scrolled = ScrolledFrame(self)
        self.scrolled.pack(fill="both", expand=True, padx=10, pady=5)

        # Kaydet butonu
        ttk.Button(self, text="Kaydet", command=self.kaydet).pack(pady=10)

        self.render_student(self.current_index)

    def render_student(self, idx):
        frame = self.scrolled.scrollable_frame
        for w in frame.winfo_children():
            w.destroy()

        if idx not in self.veri.index:
            ttk.Label(frame, text="Öğrenci bulunamadı.", foreground="red").pack(pady=10)
            return

        row = self.veri.loc[idx]
        grup = ttk.LabelFrame(frame, text=f"{row.get('Ad_Soyad', f'Satır {idx}')} ({row.get('Sınıf_Sube', '')})")
        grup.pack(fill="x", padx=10, pady=6)

        for i in range(1, 21):
            alan = f"h{i}"
            var_key = (idx, alan)
            if var_key not in self.radio_varlar:
                self.radio_varlar[var_key] = tk.StringVar(value=row.get(alan, ""))
            var = self.radio_varlar[var_key]

            satir = ttk.Frame(grup)
            satir.pack(fill="x", pady=2)
            ttk.Label(satir, text=alan, width=4).pack(side="left", padx=(0, 6))
            for secenek in self.secenekler:
                ttk.Radiobutton(satir, text=secenek, variable=var, value=secenek).pack(side="left", padx=3)

    def apply_search(self):
        term = self.search_var.get().strip()
        if term == "":
            return

        mask = self.veri["Okul_No"].astype(str).str.fullmatch(term)
        matches = self.veri[mask]

        if matches.empty:
            messagebox.showinfo("Sonuç Yok", f"{term} okul numarasıyla eşleşen öğrenci bulunamadı.")
            return

        self.current_index = matches.index[0]
        self.render_student(self.current_index)

    def kaydet(self):
        for (idx, alan), var in self.radio_varlar.items():
            if idx in self.veri.index and alan in self.veri.columns:
                self.veri.at[idx, alan] = var.get()
        try:
            self.veri.to_csv(self.hissiyat_yolu, index=False)
            messagebox.showinfo("Başarılı", "Hissiyatlar kaydedildi.")
        except Exception as e:
            messagebox.showerror("Kayıt Hatası", f"Veri kaydedilemedi:\n{e}")
        self.destroy()
