# Proje Planı: Oto Kiralama Web Sitesi (Python/Django)

Bu belge, okul ödevi için geliştirilecek oto kiralama web sitesinin geliştirme planını özetlemektedir.

## 1. Teknoloji Seçimi ve Kurulum

*   **Backend:** Python/Django
*   **Veritabanı:** SQLite (Başlangıç için)
*   **Adımlar:**
    1.  Python ve pip kurulumunu kontrol et/yap.
    2.  Proje için bir sanal ortam (virtual environment) oluştur ve aktive et (`python -m venv venv`, `source venv/bin/activate` veya `venv\Scripts\activate`).
    3.  Django'yu kur (`pip install django`).
    4.  Django projesini başlat (`django-admin startproject RooRentalCar .` - nokta önemlidir, mevcut dizine kurar).
    5.  Ana uygulamayı oluştur (`python manage.py startapp rentals`).
    6.  Oluşturulan uygulamayı `RooRentalCar/settings.py` içindeki `INSTALLED_APPS` listesine ekle.

## 2. Veritabanı Tasarımı (Django Models - `rentals/models.py`)

*   **Modeller:**
    *   **User:** Django'nun hazır `django.contrib.auth.models.User` modeli kullanılacak.
    *   **Car:**
        *   `brand` (CharField)
        *   `model` (CharField)
        *   `year` (IntegerField)
        *   `license_plate` (CharField, unique=True)
        *   `daily_rate` (DecimalField)
        *   `description` (TextField, blank=True)
        *   `image` (ImageField, `pillow` kütüphanesi gerektirir: `pip install pillow`)
        *   `is_available` (BooleanField, default=True)
    *   **Reservation:**
        *   `user` (ForeignKey to User, on_delete=models.CASCADE)
        *   `car` (ForeignKey to Car, on_delete=models.CASCADE)
        *   `start_date` (DateField)
        *   `end_date` (DateField)
        *   `total_price` (DecimalField)
        *   `status` (CharField, choices=[('pending', 'Bekliyor'), ('confirmed', 'Onaylandı'), ('cancelled', 'İptal Edildi')], default='pending')
*   **Adımlar:**
    1.  Modelleri `rentals/models.py` dosyasına yaz.
    2.  Veritabanı şemasını oluştur/güncelle:
        *   `python manage.py makemigrations rentals`
        *   `python manage.py migrate`

## 3. Backend Geliştirme (Django Views, URLs, Admin)

*   **Kullanıcı Yönetimi (`django.contrib.auth`):**
    *   Login, Logout, Signup için gerekli URL'leri ve view'ları (hazır veya özel) ayarla.
    *   Template'leri oluştur (`registration/login.html`, `registration/signup.html` vb.).
*   **Araç Yönetimi (Django Admin - `rentals/admin.py`):**
    *   `Car` modelini admin paneline kaydet (`admin.site.register(Car)`).
    *   Gerekirse `Reservation` modelini de kaydet.
    *   Bir superuser oluştur (`python manage.py createsuperuser`).
    *   `/admin` arayüzünden araçları yönet.
*   **Rezervasyon Sistemi (`rentals/views.py`, `rentals/urls.py`):**
    *   Araç listeleme (`car_list`) ve detay (`car_detail`) view'ları oluştur.
    *   Rezervasyon formu (`ReservationForm` in `rentals/forms.py`) ve işleyen view (`create_reservation`) oluştur (kullanıcı girişi gerektirir).
    *   Kullanıcının kendi rezervasyonlarını görmesi için view (`my_reservations`).
    *   İlgili URL pattern'lerini `rentals/urls.py` ve `RooRentalCar/urls.py` içinde tanımla.

## 4. Frontend Geliştirme (Django Templates - `rentals/templates/rentals/`)

*   **Temel Şablon (`base.html`):** Ortak HTML yapısı, CSS/JS linkleri, navigasyon.
*   **Sayfa Şablonları:** `index.html`, `car_list.html`, `car_detail.html`, `reservation_form.html`, `my_reservations.html`, `registration/login.html`, `registration/signup.html`.
*   **Tasarım:**
    *   Bir CSS framework (Bootstrap/Tailwind CSS) entegre et (`pip install django-bootstrap5` veya manuel).
    *   Statik dosyaları (CSS, JS, resimler) yönet (`STATIC_URL`, `STATICFILES_DIRS` ayarları).
*   **Dinamik İçerik:** Django template tag'leri (`{% %}`) ve filtreleri (`{{ | }}`) kullanarak backend verilerini göster. Formları render et.

## 5. Test ve Dağıtım

*   **Test:** Manuel olarak tüm kullanıcı akışlarını test et (kayıt, giriş, araç görme, rezervasyon yapma, admin işlemleri).
*   **Hata Ayıklama:** Geliştirme sunucusunda (`python manage.py runserver`) hataları takip et ve düzelt.
*   **Teslim:** Proje dosyalarını okulun istediği formatta hazırla. (Opsiyonel: Basit bir platforma deploy et).

## 6. Ekstra Geliştirmeler ve İleri Seviye Özellikler

## Yapılan Geliştirmeler

### Kullanıcı Profili Sayfası (Yapıldı)
* Kullanıcıların kendi bilgilerini (isim, e-posta, şifre) güncelleyebileceği, geçmiş ve mevcut rezervasyonlarını detaylı görebileceği bir profil sayfası oluşturuldu.
* Kullanıcı, profil sayfasından şifresini değiştirebiliyor.
* Kullanıcıya özel bilgiler ve rezervasyon geçmişi gösteriliyor.
* Kullanıcı profiline adres, telefon, ehliyet bilgisi, doğum tarihi ve profil fotoğrafı eklenmiştir. Kullanıcılar bu bilgileri güncelleyebilir.

### Parola Sıfırlama (Yapıldı)
* Kullanıcıların şifrelerini unuttuklarında sıfırlayabilmeleri için Django'nun hazır parola sıfırlama mekanizmaları (`django.contrib.auth.views`) entegre edildi.
* Kullanıcı, e-posta adresine gelen bağlantı ile yeni şifre belirleyebiliyor.
* Gerekli e-posta şablonları ve ayarları yapıldı.

### Test Yazımı (Yapıldı)
* Projenin kritik işlevleri (model, view erişimi, login/logout, rezervasyon oluşturma/iptal, şifre işlemleri, profil, filtreleme) için otomatik testler yazıldı.
* Django'nun test framework'ü (`unittest`) ve `Client` kullanıldı.
* Testler ile kodun doğruluğu ve güvenilirliği sağlandı, gelecekteki değişikliklerde hatalar erken tespit edilebilir.

### Kullanıcı Yönetimi ve Profil Geliştirmeleri (Yapıldı)
- Kullanıcı profiline adres, telefon, ehliyet bilgisi, doğum tarihi gibi ek alanlar eklendi. Django'nun OneToOneField ile UserProfile modeli oluşturuldu.
- Kullanıcıların profil fotoğrafı yükleyebilmesi için media ayarları genişletildi.

### Rezervasyon ve Araç Yönetimi İyileştirmeleri (Yapıldı)
- Rezervasyonlar için "beklemede", "onaylandı", "reddedildi" gibi durumlar eklendi, yönetici onay mekanizması entegre edildi.
- Araçların bakımda, müsait, kirada gibi durumlarını yönetmek için Car modeline status alanı eklendi. is_available alanı kaldırıldı, kodun tamamında tekil durum yönetimi sağlandı.
- Araçlar sadece bakımda ise listelenmiyor; kirada olsa bile farklı tarihler için kiralanabiliyor.
- Müsaitlik kontrolü, rezervasyon çakışması ile sağlanıyor; araçlar bakımda değilse her zaman listeleniyor.

## 10. Sıradaki Planlanan Geliştirmeler

*   **3. Güvenlik ve Yetkilendirme:**
    - Rezervasyon ve profil işlemlerinde, sadece ilgili kullanıcıların kendi verilerine erişebilmesi için view'larda yetkilendirme kontrolleri güçlendirilebilir.
    - Django Signals ile önemli işlemler (rezervasyon oluşturma, iptal, profil güncelleme) için loglama veya bildirim sistemi kurulabilir.

*   **4. Performans ve Ölçeklenebilirlik:**
    - Sık kullanılan sorgularda select_related ve prefetch_related kullanılarak sorgu sayısı azaltılabilir.
    - Popüler araçlar, ana sayfa gibi sık erişilen veriler için Django cache framework (Redis ile) entegre edilebilir.
    - Araç listesinde gelişmiş arama ve filtreleme (marka, model, fiyat aralığı, vites tipi vb.) eklenebilir.

*   **5. Kullanıcı Deneyimi ve Arayüz:**
    - Başarılı/başarısız işlemler için Django'nun messages framework'ü daha etkin kullanılabilir.
    - Bootstrap 5 ile responsive tasarımın yanı sıra erişilebilirlik (a11y) kontrolleri ve Lighthouse ile testler yapılabilir.
    - Kullanıcıya özel bir dashboard ile rezervasyon geçmişi, aktif rezervasyonlar, profil ayarları tek bir panelde toplanabilir.

## Görsel Plan (Mermaid)

```