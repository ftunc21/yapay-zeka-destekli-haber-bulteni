# 🧠 Yapay Zeka Destekli Haber Bülteni Oluşturucu

Bu proje, Türkiye'deki popüler haber sitelerinden güncel haberleri otomatik olarak toplayan, Google Gemini API'sini kullanarak bu haberleri önem sırasına göre sıralayan, özetleyen ve sonuçları şık bir HTML bülteni olarak sunan bir Python betiğidir.

![Örnek Bülten Görüntüsü](https://i.imgur.com/SAMPLE.jpeg)  <!-- Gerçek bir ekran görüntüsü linki ile değiştirin -->

---

## ✨ Özellikler

-   **Otomatik Veri Kazıma**: Türkiye'nin önde gelen 8+ haber sitesinden (Hürriyet, Milliyet, Sabah vb.) veri çeker.
-   **Yapay Zeka Entegrasyonu**: Google Gemini API'si ile haberleri analiz eder:
    -   Gündemdeki önem sırasına göre **sıralama**.
    -   Her haber için **tek cümlelik, dikkat çekici özetler** oluşturma.
-   **Modern HTML Raporu**: Sıralanmış ve özetlenmiş haberleri, temiz ve modern bir tasarıma sahip "haber kartları" şeklinde sunar.
-   **Esnek ve Genişletilebilir**: Yeni haber siteleri eklemek veya mevcut CSS seçicilerini güncellemek oldukça kolaydır.
-   **Hata Yönetimi**: API veya veri kazıma sırasında oluşabilecek hatalara karşı dayanıklıdır ve alternatif (standart) bir bülten oluşturabilir.
-   **Etkileşimli Arayüz**: Terminal üzerinden kullanıcıya seçenekler sunar (Bülten oluştur, Site testi yap vb.).

---

## 🚀 Kurulum

Projeyi yerel makinenizde çalıştırmak için aşağıdaki adımları izleyin.

### 1. Projeyi Klonlayın

```bash
git clone https://github.com/KULLANICI_ADINIZ/PROJE_ADINIZ.git
cd PROJE_ADINIZ
```

### 2. Gerekli Kütüphaneleri Yükleyin

Proje bağımlılıklarını `requirements.txt` dosyasını kullanarak tek komutla yükleyin:

```bash
pip install -r requirements.txt
```

### 3. Google Gemini API Anahtarını Ayarlayın

Bu projenin yapay zeka özelliklerini kullanabilmek için bir Google Gemini API anahtarına ihtiyacınız var.

-   [Google AI Studio](https://aistudio.google.com/app/apikey) adresinden ücretsiz bir API anahtarı alın.
-   Projenin ana dizininde `.env` adında bir dosya oluşturun.
-   Dosyanın içine API anahtarınızı aşağıdaki gibi ekleyin:

    ```env
    GEMINI_API_KEY="BURAYA_API_ANAHTARINIZI_YAPISTIRIN"
    ```

---

## 💻 Kullanım

Betiği çalıştırmak için terminalde aşağıdaki komutu yazmanız yeterlidir:

```bash
python news.py
```

Program size birkaç seçenek sunacaktır:

-   **1. Günlük bülten oluştur**: Tüm sitelerden haberleri çeker, Gemini ile işler ve `yapay_zeka_bulten_YYYY-MM-DD.html` adında bir dosya oluşturur.
-   **2. Tek site test et**: Belirli bir haber sitesinden veri çekilip çekilemediğini hızlıca test etmenizi sağlar.
-   **3. Tüm siteleri test et**: Tanımlı tüm sitelerin erişilebilirliğini ve veri çekme başarısını kontrol eder.
-   **4. Çıkış**: Programı sonlandırır.

Oluşturulan HTML dosyasını herhangi bir web tarayıcısında açarak bülteninizi görüntüleyebilirsiniz.

---

## 🛠️ Yapılandırma ve Genişletme

### Yeni Bir Haber Sitesi Ekleme

Yeni bir site eklemek için `news.py` dosyasındaki `HABER_SITELERI` sözlüğüne yeni bir giriş yapmanız yeterlidir:

```python
'yeni_site': {
    'url': 'https://www.yenisite.com/',
    'base_url': 'https://www.yenisite.com',
    'selector': 'a.haber-linki-stili' # Sitenin HTML yapısına uygun CSS seçici
},
```

### CSS Seçicileri Güncelleme

Eğer bir site tasarımını değiştirirse ve haberler çekilemez hale gelirse, ilgili sitenin `selector` değerini yeni HTML yapısına uygun şekilde güncellemeniz gerekebilir.

---

## 📄 Lisans

Bu proje MIT Lisansı altında lisanslanmıştır. Detaylar için `LICENSE` dosyasına göz atın. 