from fpdf import FPDF
from fpdf.enums import XPos, YPos
import os

class PDF(FPDF):
    def header(self):
        self.set_font("DejaVu", style="B", size=12)
        self.cell(0, 10, self.title, new_x=XPos.LMARGIN, new_y=YPos.NEXT, align="C")
        self.ln(5)

    def chapter_title(self, title):
        self.set_font("DejaVu", style="B", size=10)
        self.cell(0, 10, title, new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        self.ln(2)

    def chapter_body(self, body):
        self.set_font("DejaVu", size=8)
        self.multi_cell(0, 5, body)
        self.ln()

def is_text_file(filename):
    return filename.endswith(('.py', '.html', '.css', '.js', '.md', '.csv', '.json', '.txt'))

def generate_pdf_from_project(root_dir, output_pdf):
    pdf = PDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.title = "Proje Kaynak Kodları"

    # Fontları ekle
    pdf.add_font("DejaVu", style="", fname="DejaVuSans.ttf")
    pdf.add_font("DejaVu", style="B", fname="DejaVuSans-Bold.ttf")

    for foldername, subfolders, filenames in os.walk(root_dir):
        for filename in filenames:
            filepath = os.path.join(foldername, filename)

            # Sanal ortam ve dış paketleri dışla
            if ".venv" in filepath or "site-packages" in filepath:
                continue

            if is_text_file(filename):
                try:
                    with open(filepath, "r", encoding="utf-8") as f:
                        content = f.read()
                except UnicodeDecodeError:
                    try:
                        with open(filepath, "r", encoding="latin1") as f:
                            content = f.read()
                    except Exception as e:
                        print(f"Hata: {filepath} okunamadı. {e}")
                        continue

                pdf.add_page()
                pdf.chapter_title(filepath.replace(root_dir, "."))
                pdf.chapter_body(content)

    pdf.output(name=output_pdf, dest="F")

# Çalıştır
generate_pdf_from_project("./", "proje_kaynak_kodlari.pdf")