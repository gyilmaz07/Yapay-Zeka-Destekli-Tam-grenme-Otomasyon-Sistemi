from dataclasses import dataclass
from typing import Dict, Optional

@dataclass
class Student:
    okul_no: str
    ad_soyad: str
    sinif_sube: str
    cevaplar: Dict[str, Optional[str]]
    hissiyat_verileri: Dict[str, Dict[str, float]]
    istatistikler: Dict[str, int]

    def __post_init__(self):
        self.analiz_sonuclari = {}