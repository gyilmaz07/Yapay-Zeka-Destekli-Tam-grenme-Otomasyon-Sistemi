#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Optik form okuyucu ayarları

AYARLAR = {
    # Dizin yolları
    "GIRDI_DIZINI": "/home/gazy/Masaüstü/Proje_SON/optik/data/girdi/",
    "CIKTI_DIZINI": "/home/gazy/Masaüstü/Proje_SON/optik/data/cikti/",
    
    # Optik form ayarları
    "SORU_SAYISI": 20,
    "SECENEKLER": ['a', 'b', 'c', 'd', 'e'],
    
    # Görüntü işleme ayarları
    "BOS_ESIK": 0.15,    # Baloncuğun boş kabul edilmesi için maksimum doluluk oranı
    "DOLU_ESIK": 0.40,   # Baloncuğun dolu kabul edilmesi için minimum doluluk oranı
    
    # Desteklenen dosya formatları
    "DESTEKLENEN_FORMATLAR": ['*.png', '*.jpg', '*.jpeg', '*.bmp', '*.tiff']
}