import os
import json
import pandas as pd
from pathlib import Path
from typing import List, Dict, Any
from config import settings
from utils.logger import logger

def load_csv_file(file_path: Path) -> pd.DataFrame:
    """CSV dosyasını yükler"""
    try:
        if file_path.exists():
            return pd.read_csv(file_path, encoding='utf-8')
        else:
            logger.error(f"Dosya bulunamadı: {file_path}")
            return pd.DataFrame()
    except Exception as e:
        logger.error(f"CSV yükleme hatası: {e}")
        return pd.DataFrame()

def save_csv_file(file_path: Path, df: pd.DataFrame) -> bool:
    """DataFrame'i CSV dosyasına kaydeder"""
    try:
        file_path.parent.mkdir(parents=True, exist_ok=True)
        df.to_csv(file_path, index=False, encoding='utf-8')
        logger.info(f"CSV dosyası kaydedildi: {file_path}")
        return True
    except Exception as e:
        logger.error(f"CSV kaydetme hatası: {e}")
        return False

def load_json_file(file_path: Path) -> Dict[str, Any]:
    """JSON dosyasını yükler"""
    try:
        if file_path.exists():
            with open(file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        else:
            logger.error(f"JSON dosyası bulunamadı: {file_path}")
            return {}
    except Exception as e:
        logger.error(f"JSON yükleme hatası: {e}")
        return {}

def save_json_file(file_path: Path, data: Dict) -> bool:
    """JSON dosyasını kaydeder"""
    try:
        file_path.parent.mkdir(parents=True, exist_ok=True)
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
        logger.info(f"JSON dosyası kaydedildi: {file_path}")
        return True
    except Exception as e:
        logger.error(f"JSON kaydetme hatası: {e}")
        return False

def save_json_report(file_path: Path, data: Dict) -> bool:
    """JSON rapor dosyasını kaydeder (save_json_file ile aynı)"""
    return save_json_file(file_path, data)

def save_html_report(file_path: Path, html_content: str) -> bool:
    """HTML raporunu kaydeder"""
    try:
        file_path.parent.mkdir(parents=True, exist_ok=True)
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
        logger.info(f"HTML raporu kaydedildi: {file_path}")
        return True
    except Exception as e:
        logger.error(f"HTML kaydetme hatası: {e}")
        return False

def find_optik_files() -> List[Path]:
    """Optik cevap dosyalarını bulur"""
    try:
        optik_files = []
        optik_dir = settings.OPTIK_CEVAPLAR_DIR
        
        if not optik_dir.exists():
            logger.warning(f"Optik cevaplar dizini bulunamadı: {optik_dir}")
            return []
            
        for file in optik_dir.iterdir():
            if file.name.startswith('sonuc_') and file.suffix == '.json':
                optik_files.append(file)
                
        logger.info(f"{len(optik_files)} optik dosya bulundu")
        return optik_files
        
    except Exception as e:
        logger.error(f"Optik dosya bulma hatası: {e}")
        return []

def get_student_files() -> List[Path]:
    """Öğrenci CSV dosyalarını bulur"""
    try:
        student_files = []
        student_dir = settings.OGRENCI_PATH.parent
        
        if not student_dir.exists():
            logger.warning(f"Öğrenci dizini bulunamadı: {student_dir}")
            return []
            
        for file in student_dir.iterdir():
            if file.suffix == '.csv':
                student_files.append(file)
                
        return student_files
        
    except Exception as e:
        logger.error(f"Öğrenci dosyası bulma hatası: {e}")
        return []
