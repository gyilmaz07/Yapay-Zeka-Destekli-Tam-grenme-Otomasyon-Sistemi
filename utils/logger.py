import logging
import os
from pathlib import Path
from config import settings

def setup_logger():
    """Loglama sistemini kurar"""
    # Log dizinini oluştur
    settings.LOG_DIR.mkdir(parents=True, exist_ok=True)

    # Logger'ı yapılandır
    logger = logging.getLogger('tam_ogrenme_otomasyonu')
    logger.setLevel(logging.INFO)

    # Dosya handler'ı
    file_handler = logging.FileHandler(settings.LOG_FILE)
    file_handler.setLevel(logging.INFO)

    # Konsol handler'ı
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)

    # Formatter
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)

    # Handler'ları ekle
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    return logger

# Global logger instance'ı oluştur
logger = setup_logger()