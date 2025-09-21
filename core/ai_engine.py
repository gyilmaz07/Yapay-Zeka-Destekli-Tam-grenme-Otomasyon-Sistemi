from typing import Dict, List
from config import settings
from utils.logger import logger
from models.question import Question
from models.result import AnalysisResult
from models.student import Student

class AIEngine:
    def __init__(self):
        self.questions = []
        
    def set_questions(self, questions: List[Question]):
        """Analiz için soruları ayarla"""
        self.questions = questions
        
    def analyze_student(self, student: Student) -> List[AnalysisResult]:
        """Öğrenci cevaplarını analiz eder"""
        results = []
        
        for question in self.questions:
            soru_no = question.soru_no
            soru_no_str = str(soru_no)
            
            ogrenci_cevap = student.cevaplar.get(soru_no_str)
            
            # CSV'den gelen hissiyat verilerini al
            hissiyat = student.hissiyat_verileri.get(soru_no_str, "belirsiz")
            
            # Hissiyat değerini normalize et
            hissiyat = self._normalize_sentiment(hissiyat)
            
            # Güven endeksi hesapla
            guven_endeksi = self._calculate_confidence_csv(hissiyat, ogrenci_cevap, question.dogru_cevap)
            
            # Zorluk seviyesini belirle
            zorluk_seviyesi = self._determine_difficulty_level(hissiyat, ogrenci_cevap, question.dogru_cevap)
            
            # Durumu belirle
            durum = self._determine_status(ogrenci_cevap, question.dogru_cevap)
            
            # Tavsiye oluştur
            tavsiye = self._generate_recommendation(
                durum,
                hissiyat,
                guven_endeksi,
                question.tema_adi
            )
            
            result = AnalysisResult(
                soru_no=soru_no,
                ogrenci_cevap=ogrenci_cevap,
                dogru_cevap=question.dogru_cevap,
                durum=durum,
                hissiyat=hissiyat,
                tema_adi=question.tema_adi,
                ogrenme_ciktisi=question.ogrenme_ciktisi,
                zorluk_seviyesi=zorluk_seviyesi,
                guven_endeksi=guven_endeksi,
                tavsiye=tavsiye,
                ogrenme_baglantisi=question.ogrenme_baglantisi  # ✅ Yeni eklenen alan
            )
            
            results.append(result)
            
        return results
        
    def _normalize_sentiment(self, hissiyat: str) -> str:
        """Hissiyat değerlerini standartlaştırır"""
        hissiyat = hissiyat.lower().strip()
        
        sentiment_mapping = {
            "çok kolay": "çok kolay",
            "kolay": "kolay",
            "orta": "orta",
            "zor": "zor",
            "çok zor": "çok zor",
            "anlamadım": "anlamadım",
            "belirsiz": "belirsiz",
            "": "belirsiz"
        }
        
        return sentiment_mapping.get(hissiyat, "belirsiz")
        
    def _calculate_confidence_csv(self, hissiyat: str, ogrenci_cevap: str, dogru_cevap: str) -> float:
        """CSV hissiyat verileri için güven endeksi hesaplar"""
        durum = self._determine_status(ogrenci_cevap, dogru_cevap)
        
        hissiyat_guven_map = {
            "çok kolay": 0.9,
            "kolay": 0.7,
            "orta": 0.5,
            "zor": 0.3,
            "çok zor": 0.1,
            "anlamadım": 0.1,
            "belirsiz": 0.5
        }
        
        base_guven = hissiyat_guven_map.get(hissiyat, 0.5)
        
        # Duruma göre ayarlama
        if durum == "Doğru":
            return min(1.0, base_guven + 0.2)
        elif durum == "Yanlış":
            return max(0.0, base_guven - 0.2)
        else:  # Boş
            return max(0.0, base_guven - 0.3)
            
    def _determine_status(self, ogrenci_cevap: str, dogru_cevap: str) -> str:
        """Cevap durumunu belirler"""
        if not ogrenci_cevap or ogrenci_cevap.strip() == "":
            return "Boş"
        elif ogrenci_cevap.upper() == dogru_cevap.upper():
            return "Doğru"
        else:
            return "Yanlış"
                
    def _determine_difficulty_level(self, hissiyat: str, ogrenci_cevap: str, dogru_cevap: str) -> str:
        """Zorluk seviyesini belirler"""
        durum = self._determine_status(ogrenci_cevap, dogru_cevap)
        
        if hissiyat in ["çok kolay", "kolay"] and durum == "Doğru":
            return "Kolay"
        elif hissiyat in ["zor", "çok zor", "anlamadım"] and durum == "Yanlış":
            return "Zor"
        else:
            return "Orta"
            
    def _generate_recommendation(self, durum: str, hissiyat: str, guven_endeksi: float, tema: str) -> str:
        """Öğrenci için tavsiye oluşturur"""
        recommendations = {
            ("Boş", "any"): f"{tema} konusunu tekrar gözden geçirmeniz önerilir.",
            ("any", "anlamadım"): f"{tema} konusunda temel eksiğiniz var. Öğretmeninizle görüşmeniz faydalı olacaktır.",
            ("Yanlış", "any"): f"{tema} konusunda yanlış anlaşılmalar var. Konuyu tekrar çalışmanız önerilir.",
            ("Doğru", "çok kolay"): f"{tema} konusunu mükemmel anlamışsınız! Bir sonraki konuya geçebilirsiniz.",
            ("Doğru", "kolay"): f"{tema} konusunu iyi anlamışsınız. Pratik yapmaya devam edin.",
            ("Doğru", "orta"): f"{tema} konusunu anlamışsınız. Daha fazla pratik yaparak pekiştirebilirsiniz.",
            ("Doğru", "zor"): f"{tema} konusunu anlamışsınız ancak zorlandınız. Ek çalışma faydalı olacaktır.",
            ("Doğru", "çok zor"): f"{tema} konusunu anlamışsınız ama çok zorlandınız. Öğretmeninizden destek alabilirsiniz."
        }
        
        # Özel durumlar için kontrol
        for (d, h), recommendation in recommendations.items():
            if (d == durum or d == "any") and (h == hissiyat or h == "any"):
                return recommendation
        
        # Varsayılan tavsiye
        return f"{tema} konusunda ortalama performans gösterdiniz. Pratik yapmaya devam edin."