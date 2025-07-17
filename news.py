#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Türkiye Haber Bülteni Otomasyonu
Günlük haber toplama ve bülten oluşturma aracı
"""

import requests
from bs4 import BeautifulSoup
import datetime
import json
import time
import os
from urllib.parse import urljoin, urlparse
import google.generativeai as genai
from dotenv import load_dotenv

# .env dosyasından API anahtarını yükle
load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)
else:
    print("⚠️  Uyarı: GEMINI_API_KEY bulunamadı. Lütfen .env dosyasını kontrol edin.")

# Haber sitelerinin URL'leri ve CSS seçicileri
HABER_SITELERI = {
    'hurriyet': {
        'url': 'https://www.hurriyet.com.tr/',
        'base_url': 'https://www.hurriyet.com.tr',
        'selector': 'a[href*="/gundem/"], a[href*="/ekonomi/"], a[href*="/spor/"]'
    },
    'milliyet': {
        'url': 'https://www.milliyet.com.tr/',
        'base_url': 'https://www.milliyet.com.tr',
        'selector': 'a[href*="/gundem/"], a[href*="/ekonomi/"], a[href*="/spor/"]'
    },
    'sabah': {
        'url': 'https://www.sabah.com.tr/',
        'base_url': 'https://www.sabah.com.tr',
        'selector': 'a[href*="/gundem"], a[href*="/ekonomi"], a[href*="/spor"]'
    },
    'sozcu': {
        'url': 'https://www.sozcu.com.tr/',
        'base_url': 'https://www.sozcu.com.tr',
        'selector': 'a[href*="/gundem"], a[href*="/ekonomi"], a[href*="/spor"]'
    },
    'haberturk': {
        'url': 'https://www.haberturk.com/',
        'base_url': 'https://www.haberturk.com',
        'selector': 'a[href*="/gundem"], a[href*="/ekonomi"], a[href*="/spor"]'
    },
    'ntv': {
        'url': 'https://www.ntv.com.tr/',
        'base_url': 'https://www.ntv.com.tr',
        'selector': 'a[href*="/turkiye"], a[href*="/ekonomi"], a[href*="/spor"]'
    },
    'cnnturk': {
        'url': 'https://www.cnnturk.com/',
        'base_url': 'https://www.cnnturk.com',
        'selector': 'a[href*="/turkiye"], a[href*="/ekonomi"], a[href*="/spor"]'
    },
    'trt': {
        'url': 'https://www.trthaber.com/',
        'base_url': 'https://www.trthaber.com',
        'selector': 'a[href*="/gundem"], a[href*="/ekonomi"], a[href*="/spor"]'
    }
}

# Headers - Bazı siteler bot tespitini engellemek için
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
}

def haber_cek(site_adi, max_haber=10):
    """
    Belirtilen haber sitesinden haberleri çeker
    
    Args:
        site_adi (str): HABER_SITELERI dictionary'sindeki site adı
        max_haber (int): Maksimum çekilecek haber sayısı
    
    Returns:
        list: [(başlık, link, site_adi)] formatında haberler
    """
    if site_adi not in HABER_SITELERI:
        print(f"❌ Hata: {site_adi} sitesi tanımlı değil!")
        return []
    
    site_config = HABER_SITELERI[site_adi]
    haberler = []
    
    try:
        print(f"📰 {site_adi.upper()} sitesinden haberler çekiliyor...")
        
        # HTTP isteği gönder
        response = requests.get(site_config['url'], headers=HEADERS, timeout=10)
        response.raise_for_status()  # HTTP hatalarını yakala
        
        # HTML'i parse et
        soup = BeautifulSoup(response.content, 'lxml')
        
        # CSS seçici ile haberleri bul
        haber_linkleri = soup.select(site_config['selector'])
        
        for i, link in enumerate(haber_linkleri[:max_haber]):
            try:
                # Başlık al
                baslik = link.get_text(strip=True)
                if not baslik:
                    continue
                
                # Link al ve tam URL'e dönüştür
                href = link.get('href')
                if not href:
                    continue
                
                if href.startswith('http'):
                    tam_link = href
                else:
                    tam_link = urljoin(site_config['base_url'], href)
                
                # Başlık minimum uzunlukta olmalı
                if len(baslik) > 10:
                    haberler.append((baslik, tam_link, site_adi))
                    
            except Exception as e:
                print(f"⚠️  Haber işlenirken hata: {e}")
                continue
        
        print(f"✅ {site_adi}: {len(haberler)} haber çekildi")
        return haberler
        
    except requests.RequestException as e:
        print(f"❌ {site_adi} sitesine bağlantı hatası: {e}")
        return []
    except Exception as e:
        print(f"❌ {site_adi} işlenirken beklenmeyen hata: {e}")
        return []

def tum_haberleri_topla(site_basina_max=10):
    """
    Tüm tanımlı haber sitelerinden haberleri toplar
    
    Args:
        site_basina_max (int): Her siteden maksimum kaç haber çekilecek
    
    Returns:
        dict: Her site için haberlerin bulunduğu dictionary
    """
    print("🚀 Günlük haber toplama işlemi başlıyor...")
    print("=" * 50)
    
    tum_haberler = {}
    toplam_haber_sayisi = 0
    
    for site_adi in HABER_SITELERI.keys():
        # Her site arasında kısa bir bekleme (sitelerimizin aşırı yüklenmemesi için)
        time.sleep(1)
        
        haberler = haber_cek(site_adi, site_basina_max)
        if haberler:
            tum_haberler[site_adi] = haberler
            toplam_haber_sayisi += len(haberler)
        else:
            tum_haberler[site_adi] = []
    
    print(f"🎉 Toplam {toplam_haber_sayisi} haber {len(HABER_SITELERI)} siteden toplandı!")
    return tum_haberler

def haberleri_gemini_ile_isle(haberler_dict):
    """
    Toplanan haberleri Gemini'ye göndererek önem sırasına göre sıralatır ve özetletir.
    """
    if not GEMINI_API_KEY:
        print("❌ Gemini API anahtarı ayarlanmamış. İşlem atlanıyor.")
        return None

    print("🧠 Haberler Gemini'ye gönderiliyor, lütfen bekleyin...")
    
    # Haberleri Gemini'nin işleyebileceği basit bir metin formatına dönüştür
    ham_metin = ""
    for site, haberler in haberler_dict.items():
        for baslik, link, _ in haberler:
            ham_metin += f"Başlık: {baslik}\nLink: {link}\nKaynak: {site}\n---\n"
            
    # Gemini için model ve prompt hazırlığı
    model = genai.GenerativeModel('gemini-2.5-flash')
    
    prompt = f"""
    Aşağıda Türkiye'deki farklı haber sitelerinden toplanmış güncel haber başlıkları bulunmaktadır. 
    Bu haberleri analiz et ve aşağıdaki görevleri yerine getir:

    1.  Tüm haberleri Türkiye gündemindeki önem sırasına göre **en önemliden en önemsize** doğru sırala.
    2.  Her haber için **tek cümlelik, dikkat çekici bir özet** oluştur.
    3.  Sonucu, her haber için bir JSON nesnesi içeren bir JSON dizisi olarak formatla. Her JSON nesnesi şu alanları içermeli: "sira", "baslik", "link", "kaynak", "ozet".

    İşte haberler:
    ---
    {ham_metin}
    ---
    Lütfen çıktıyı sadece JSON formatında, başka hiçbir ek metin olmadan ver.
    """
    
    try:
        response = model.generate_content(prompt)
        # Gemini'nin çıktısındaki markdown formatını temizle
        json_yanit = response.text.strip().replace("```json", "").replace("```", "")
        return json.loads(json_yanit)
    except Exception as e:
        print(f"❌ Gemini API ile konuşurken bir hata oluştu: {e}")
        print("--- Gemini Ham Yanıt ---")
        print(response.text)
        print("-----------------------")
        return None

def yeni_bulten_olustur(islenmis_haberler):
    """
    Gemini tarafından işlenmiş haberlerden gelişmiş HTML bülteni oluşturur.
    """
    tarih = datetime.datetime.now().strftime("%d %B %Y - %A")
    
    html_content = f"""
    <!DOCTYPE html>
    <html lang="tr">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Yapay Zeka Destekli Günlük Haber Bülteni - {tarih}</title>
        <style>
            body {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif; line-height: 1.6; margin: 0; padding: 20px; background-color: #f0f2f5; color: #1c1e21; }}
            .container {{ max-width: 700px; margin: 20px auto; background: #fff; border-radius: 12px; box-shadow: 0 4px 12px rgba(0,0,0,0.1); overflow: hidden; }}
            .header {{ background-color: #4a90e2; color: white; padding: 30px; text-align: center; }}
            .header h1 {{ margin: 0; font-size: 28px; }}
            .header p {{ margin: 5px 0 0; opacity: 0.9; }}
            .content {{ padding: 30px; }}
            .haber-kart {{ border: 1px solid #dddfe2; border-radius: 10px; margin-bottom: 20px; padding: 20px; transition: box-shadow 0.3s ease; }}
            .haber-kart:hover {{ box-shadow: 0 4px 15px rgba(0,0,0,0.15); }}
            .haber-kart .sira {{ font-size: 24px; font-weight: bold; color: #4a90e2; float: left; margin-right: 15px; line-height: 1; }}
            .haber-kart .meta {{ font-size: 13px; color: #606770; margin-bottom: 8px; text-transform: uppercase; }}
            .haber-kart h2 {{ font-size: 18px; margin: 0 0 10px; }}
            .haber-kart h2 a {{ color: #050505; text-decoration: none; }}
            .haber-kart h2 a:hover {{ text-decoration: underline; }}
            .haber-kart .ozet {{ font-size: 15px; color: #333; }}
            .footer {{ text-align: center; padding: 20px; font-size: 12px; color: #8a8d91; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>🧠 Yapay Zeka Destekli Haber Bülteni</h1>
                <p>{tarih}</p>
            </div>
            <div class="content">
    """

    if not islenmis_haberler:
         html_content += "<p>Bugün işlenecek haber bulunamadı veya bir hata oluştu.</p>"
    else:
        for haber in islenmis_haberler:
            html_content += f"""
                <div class="haber-kart">
                    <div class="sira">{haber.get('sira', '')}</div>
                    <div>
                        <div class="meta">Kaynak: {haber.get('kaynak', 'Bilinmiyor').upper()}</div>
                        <h2><a href="{haber.get('link', '#')}" target="_blank">{haber.get('baslik', 'Başlık Yok')}</a></h2>
                        <p class="ozet">{haber.get('ozet', 'Özet bulunamadı.')}</p>
                    </div>
                </div>
            """

    html_content += """
            </div>
            <div class="footer">
                Bu bülten, haber sitelerinden toplanan verilerin Gemini API ile işlenmesiyle otomatik olarak oluşturulmuştur.
            </div>
        </div>
    </body>
    </html>
    """
    return html_content

def gunluk_bulten_olustur():
    """
    Ana fonksiyon: Günlük bülteni oluşturur, Gemini ile işler ve dosyaya kaydeder
    """
    try:
        bugun = datetime.datetime.now()
        
        print(f"📅 {bugun.strftime('%d %B %Y %A')} tarihli bülten oluşturuluyor...")
        
        # 1. Ham haberleri topla
        ham_haberler = tum_haberleri_topla(site_basina_max=10)
        
        if not any(ham_haberler.values()):
            print("Hiçbir siteden haber çekilemedi. İşlem durduruluyor.")
            return

        # 2. Gemini ile işle
        islenmis_haberler = haberleri_gemini_ile_isle(ham_haberler)
        
        # 3. Yeni HTML bülteni oluştur
        if islenmis_haberler:
            html_icerik = yeni_bulten_olustur(islenmis_haberler)
            dosya_adi = f"yapay_zeka_bulten_{bugun.strftime('%Y-%m-%d')}.html"
        else:
            print("⚠️ Gemini'den geçerli bir yanıt alınamadı. Standart bülten oluşturuluyor.")
            html_icerik = haber_bultenini_olustur(ham_haberler) # Eski bülteni oluştur
            dosya_adi = f"standart_bulten_{bugun.strftime('%Y-%m-%d')}.html"

        # 4. Dosyaya kaydet
        with open(dosya_adi, 'w', encoding='utf-8') as f:
            f.write(html_icerik)
        
        print(f"✅ Bülten başarıyla oluşturuldu: {dosya_adi}")
        print(f"🌐 Dosyayı tarayıcınızda açmak için: file://{os.path.abspath(dosya_adi)}")
        
    except Exception as e:
        print(f"❌ Bülten oluşturulurken genel bir hata oluştu: {e}")


def haber_bultenini_olustur(haberler_dict):
    """
    Toplanan haberlerden HTML bülteni oluşturur
    
    Args:
        haberler_dict (dict): Site adı -> haberler listesi
    
    Returns:
        str: HTML formatında bülten
    """
    tarih = datetime.datetime.now().strftime("%d %B %Y - %A")
    
    html_content = f"""
    <!DOCTYPE html>
    <html lang="tr">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Günlük Haber Bülteni - {tarih}</title>
        <style>
            body {{
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                line-height: 1.6;
                margin: 0;
                padding: 20px;
                background-color: #f5f5f5;
            }}
            .container {{
                max-width: 800px;
                margin: 0 auto;
                background: white;
                padding: 30px;
                border-radius: 10px;
                box-shadow: 0 0 20px rgba(0,0,0,0.1);
            }}
            h1 {{
                color: #2c3e50;
                text-align: center;
                border-bottom: 3px solid #3498db;
                padding-bottom: 10px;
            }}
            h2 {{
                color: #e74c3c;
                margin-top: 30px;
                text-transform: uppercase;
                font-size: 1.2em;
            }}
            .haber-item {{
                margin-bottom: 15px;
                padding: 10px;
                background: #f8f9fa;
                border-left: 4px solid #3498db;
                border-radius: 5px;
            }}
            .haber-item a {{
                text-decoration: none;
                color: #2c3e50;
                font-weight: bold;
                display: block;
                margin-bottom: 5px;
            }}
            .haber-item a:hover {{
                color: #3498db;
            }}
            .kaynak {{
                font-size: 0.8em;
                color: #7f8c8d;
                text-transform: uppercase;
            }}
            .footer {{
                text-align: center;
                margin-top: 40px;
                padding-top: 20px;
                border-top: 1px solid #ecf0f1;
                color: #7f8c8d;
                font-size: 0.9em;
            }}
            .stats {{
                background: #ecf0f1;
                padding: 15px;
                border-radius: 5px;
                text-align: center;
                margin-bottom: 20px;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <h1>📰 Günlük Haber Bülteni</h1>
            <div class="stats">
                <strong>{tarih}</strong><br>
                Toplam {sum(len(haberler) for haberler in haberler_dict.values())} haber, 
                {len([site for site, haberler in haberler_dict.items() if haberler])} kaynaktan
            </div>
    """
    
    # Her site için haberleri ekle
    for site_adi, haberler in haberler_dict.items():
        if haberler:  # Eğer siteden haber çekildiyse
            html_content += f"\n            <h2>📰 {site_adi.upper()}</h2>\n"
            
            for baslik, link, kaynak in haberler:
                html_content += f"""
            <div class="haber-item">
                <a href="{link}" target="_blank">{baslik}</a>
                <div class="kaynak">Kaynak: {kaynak}</div>
            </div>"""
    
    html_content += """
        </div>
        <div class="footer">
            Bu bülten otomatik olarak oluşturulmuştur.<br>
            Python BeautifulSoup ile web scraping
        </div>
    </body>
    </html>
    """
    
    return html_content

def site_testi(site_adi):
    """
    Tek bir siteyi test etmek için yardımcı fonksiyon
    """
    print(f"🧪 {site_adi} sitesi test ediliyor...")
    haberler = haber_cek(site_adi, max_haber=3)
    
    if haberler:
        print(f"✅ Test başarılı! {len(haberler)} haber bulundu:")
        for i, (baslik, link, kaynak) in enumerate(haberler, 1):
            print(f"  {i}. {baslik[:80]}...")
    else:
        print(f"❌ Test başarısız - haber bulunamadı")

# Ana Program
if __name__ == "__main__":
    print("🗞️  TÜRKİYE HABER BÜLTENİ OTOMASYONU")
    print("=" * 40)
    
    while True:
        print("\nNe yapmak istiyorsunuz?")
        print("1. Günlük bülten oluştur")
        print("2. Tek site test et") 
        print("3. Tüm siteleri test et")
        print("4. Çıkış")
        
        secim = input("\nSeçiminizi yapın (1-4): ").strip()
        
        if secim == "1":
            gunluk_bulten_olustur()
            
        elif secim == "2":
            print("\nMevcut siteler:")
            for i, site in enumerate(HABER_SITELERI.keys(), 1):
                print(f"  {i}. {site}")
            
            try:
                site_no = int(input("Test etmek istediğiniz site numarası: ")) - 1
                site_listesi = list(HABER_SITELERI.keys())
                if 0 <= site_no < len(site_listesi):
                    site_testi(site_listesi[site_no])
                else:
                    print("❌ Geçersiz site numarası!")
            except ValueError:
                print("❌ Lütfen geçerli bir numara girin!")
                
        elif secim == "3":
            print("🧪 Tüm siteler test ediliyor...")
            for site in HABER_SITELERI.keys():
                site_testi(site)
                print("-" * 30)
                
        elif secim == "4":
            print("👋 Görüşmek üzere!")
            break
            
        else:
            print("❌ Geçersiz seçim! Lütfen 1-4 arası bir sayı girin.")
