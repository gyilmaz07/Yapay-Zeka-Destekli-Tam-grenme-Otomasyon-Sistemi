#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
from datetime import datetime

def create_answer_sheet():
    # Çıktı dizinini kontrol et ve yoksa oluştur
    output_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'cikti')
    os.makedirs(output_dir, exist_ok=True)
    
    # Çıktı dosyası için zaman damgası ekle
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = os.path.join(output_dir, f'optik_cevap_formu_{timestamp}.svg')
    
    # SVG içeriği
    svg_content = f'''<svg width="800" height="1100" xmlns="http://www.w3.org/2000/svg">
    <rect width="100%" height="100%" fill="white"/>
    
    <!-- Başlık ve bilgi alanları -->
    <text x="400" y="40" text-anchor="middle" font-family="Arial, sans-serif" font-size="20" font-weight="bold">OPTİK CEVAP FORMU</text>
    <text x="200" y="70" text-anchor="start" font-family="Arial, sans-serif" font-size="14">Sınıf/Şube:</text>
    <line x1="250" y1="72" x2="400" y2="72" stroke="black"/>
    <text x="450" y="70" text-anchor="start" font-family="Arial, sans-serif" font-size="14">Okul No:</text>
    <line x1="500" y1="72" x2="650" y2="72" stroke="black"/>
    
    <!-- Seçenek başlıkları -->
    <text x="120" y="100" text-anchor="middle" font-family="Arial, sans-serif" font-size="12">Soru</text>
    <text x="170" y="100" text-anchor="middle" font-family="Arial, sans-serif" font-size="12">a</text>
    <text x="200" y="100" text-anchor="middle" font-family="Arial, sans-serif" font-size="12">b</text>
    <text x="230" y="100" text-anchor="middle" font-family="Arial, sans-serif" font-size="12">c</text>
    <text x="260" y="100" text-anchor="middle" font-family="Arial, sans-serif" font-size="12">d</text>
    <text x="290" y="100" text-anchor="middle" font-family="Arial, sans-serif" font-size="12">e</text>
    
    <text x="450" y="100" text-anchor="middle" font-family="Arial, sans-serif" font-size="12">Soru</text>
    <text x="500" y="100" text-anchor="middle" font-family="Arial, sans-serif" font-size="12">a</text>
    <text x="530" y="100" text-anchor="middle" font-family="Arial, sans-serif" font-size="12">b</text>
    <text x="560" y="100" text-anchor="middle" font-family="Arial, sans-serif" font-size="12">c</text>
    <text x="590" y="100" text-anchor="middle" font-family="Arial, sans-serif" font-size="12">d</text>
    <text x="620" y="100" text-anchor="middle" font-family="Arial, sans-serif" font-size="12">e</text>
    
    <!-- Soru numaraları ve baloncuklar - İlk sütun (1-10) -->
    '''
    
    # İlk sütun (1-10)
    for i in range(1, 11):
        y_pos = 120 + (i-1)*30
        svg_content += f'<text x="120" y="{y_pos}" text-anchor="middle" font-family="Arial, sans-serif" font-size="12">{i}</text>\n'
        
        # Baloncuklar
        for j, letter in enumerate(['a', 'b', 'c', 'd', 'e']):
            x_pos = 170 + j*30
            svg_content += f'<circle cx="{x_pos}" cy="{y_pos-5}" r="8" fill="none" stroke="black"/>\n'
    
    # İkinci sütun (11-20)
    for i in range(11, 21):
        y_pos = 120 + (i-11)*30
        svg_content += f'<text x="450" y="{y_pos}" text-anchor="middle" font-family="Arial, sans-serif" font-size="12">{i}</text>\n'
        
        # Baloncuklar
        for j, letter in enumerate(['a', 'b', 'c', 'd', 'e']):
            x_pos = 500 + j*30
            svg_content += f'<circle cx="{x_pos}" cy="{y_pos-5}" r="8" fill="none" stroke="black"/>\n'
    
    # Hizalama işaretleri
    svg_content += '''
    <!-- Hizalama işaretleri -->
    <circle cx="50" cy="50" r="5" fill="black"/>
    <circle cx="750" cy="50" r="5" fill="black"/>
    <circle cx="50" cy="1050" r="5" fill="black"/>
    <circle cx="750" cy="1050" r="5" fill="black"/>
    '''
    
    # Talimatlar
    svg_content += '''
    <!-- Talimatlar -->
    <text x="400" y="1070" text-anchor="middle" font-family="Arial, sans-serif" font-size="10">
        Doğru cevabı işaretlemek için ilgili baloncuğu tamamen doldurunuz.
    </text>
    <text x="400" y="1085" text-anchor="middle" font-family="Arial, sans-serif" font-size="10">
        Birden fazla işaretleme yapmayınız ve işaretlerinizi düzgün yapınız.
    </text>
    '''
    
    svg_content += '</svg>'
    
    # SVG içeriğini dosyaya yaz
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(svg_content)
    
    print(f"Optik cevap formu '{output_file}' olarak oluşturuldu.")
    return output_file

if __name__ == "__main__":
    # Çalışma dizinini kontrol et
    current_dir = os.path.dirname(os.path.abspath(__file__))
    expected_dir = os.path.join(os.path.dirname(os.path.dirname(current_dir)), 'src')
    
    if current_dir != expected_dir:
        print(f"Uyarı: Kodun '{expected_dir}' dizininde çalıştırılması önerilir.")
        print(f"Şu anki dizin: {current_dir}")
        
        # Devam etmek isteyip istemediğini sor
        response = input("Devam etmek istiyor musunuz? (e/h): ").lower()
        if response != 'e':
            print("İşlem iptal edildi.")
            sys.exit(1)
    
    create_answer_sheet()