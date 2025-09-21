# utils/print_utils.py
from pathlib import Path
import subprocess
import tempfile
import shutil
from typing import Optional, List
from utils.logger import logger

try:
    import cairosvg
except Exception:
    cairosvg = None

def convert_svg_to_pdf(svg_path: Path, pdf_path: Path) -> bool:
    """SVG'yi PDF'e dönüştür (cairosvg ile)."""
    try:
        if cairosvg is None:
            logger.error("cairosvg bulunamadı. 'pip install cairosvg' ile yükleyin.")
            return False
        cairosvg.svg2pdf(url=str(svg_path), write_to=str(pdf_path))
        return True
    except Exception as e:
        logger.error(f"SVG->PDF dönüştürme hatası ({svg_path.name}): {e}")
        return False

def print_pdf_with_lp(pdf_path: Path, printer: Optional[str] = None, copies: int = 1) -> bool:
    """PDF'i CUPS üzerinden yazdır (lp komutu ile)."""
    try:
        cmd: List[str] = ["lp", "-n", str(copies)]
        if printer:
            cmd += ["-d", printer]
        cmd.append(str(pdf_path))
        subprocess.run(cmd, check=True)
        return True
    except subprocess.CalledProcessError as e:
        logger.error(f"Yazdırma hatası (lp): {e}")
        return False
    except FileNotFoundError:
        logger.error("lp komutu bulunamadı. CUPS kurulu mu?")
        return False

def print_all_svgs_in_dir(svg_dir: Path, printer: Optional[str] = None, copies: int = 1) -> int:
    """
    Klasördeki tüm .svg dosyalarını PDF'e çevirip yazdırır.
    Başarılı gönderim sayısını döndürür.
    """
    if not svg_dir.exists():
        logger.error(f"SVG klasörü bulunamadı: {svg_dir}")
        return 0

    svg_files = sorted([p for p in svg_dir.iterdir() if p.suffix.lower() == ".svg"])
    if not svg_files:
        logger.info(f"Klasörde SVG bulunamadı: {svg_dir}")
        return 0

    success_count = 0
    with tempfile.TemporaryDirectory(prefix="svg_print_") as tmpdir:
        tmpdir_path = Path(tmpdir)
        for svg_path in svg_files:
            pdf_path = tmpdir_path / (svg_path.stem + ".pdf")
            if not convert_svg_to_pdf(svg_path, pdf_path):
                continue
            if print_pdf_with_lp(pdf_path, printer=printer, copies=copies):
                success_count += 1
            else:
                # Dönüştürülmüş PDF'i saklamak isterseniz buraya kopyalayabilirsiniz
                # shutil.copy2(pdf_path, svg_path.parent / (svg_path.stem + "_FAILED.pdf"))
                pass

    logger.info(f"Yazıcıya gönderildi: {success_count}/{len(svg_files)}")
    return success_count
