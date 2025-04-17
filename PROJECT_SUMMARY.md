# RooRentalCar Proje Özeti ve Özellikleri

## Proje Amacı
Modern ve kullanıcı dostu bir arayüze sahip, araç kiralama işlemlerini yöneten bir web uygulaması oluşturmak.

## Genel Yapı ve Uygulamalar
1.  **Django Projesi:** Temel yapı Django framework'ü üzerine kurulu.
2.  **`rentals` Uygulaması:** Araçlar, rezervasyonlar, kullanıcı profili gibi temel kiralama işlevlerini barındırıyor.
3.  **`core` Uygulaması:** Ana sayfa, hakkımızda, iletişim gibi genel site sayfalarını ve işlevlerini yönetiyor.
4.  **Standart Django Mimarisi:** `settings.py`, `urls.py`, MVT (Model-View-Template) yapısı takip ediliyor.

## Öne Çıkan Özellikler ve Geliştirmeler

### 1. Kullanıcı Yönetimi
-   Django'nun yerleşik kullanıcı modeli kullanılıyor.
-   Kayıt olma (Signup) ve Giriş/Çıkış (Login/Logout) işlevleri mevcut.
-   Şifre değiştirme bağlantısı profil sayfasında yer alıyor.

### 2. Ana Sayfa (`core`)
-   **Modern Tasarım:** 
    -   Özel renk paleti (Koyu arduvaz mavisi, turkuaz, beyaz, griler).
    -   Modern fontlar (`Montserrat`, `Open Sans` - Google Fonts).
    -   Geniş beyaz alanlar ve düzenli yerleşim.
-   **Dinamik İçerik:**
    -   "Popüler Araçlar" bölümü: Veritabanından en yeni 3 müsait aracı dinamik olarak çeker (varsayılan resim desteğiyle).
    -   Dinamik Müşteri Yorumları (Testimonial) kaydırıcısı.
-   **Animasyonlar:** AOS (Animate On Scroll) kütüphanesi ile yumuşak animasyonlar.
-   **Yapı:** Hero alanı, avantajlar bölümü, popüler araçlar, müşteri yorumları.

### 3. Araç İşlemleri (`rentals`)
-   **Araç Listeleme:** Tüm kiralanabilir araçların listelendiği sayfa (`car_list`).
-   **Araç Detay:** Seçilen aracın detaylarının gösterildiği sayfa (`car_detail`).
-   `Car` modeli veritabanında araç bilgilerini tutar.
-   **Araç Durum Yönetimi:** Araçlar için `status` alanı ("available", "maintenance", "rented") ile bakımda olan araçlar listelenmez, diğer tüm araçlar (kirada olsa bile) listelenir ve uygun tarihler için kiralanabilir.
-   **is_available Alanı Kaldırıldı:** Kodun tamamında tekil durum yönetimi sağlandı, veri tutarlılığı artırıldı.

### 4. Rezervasyon İşlemleri (`rentals`)
-   **Rezervasyon Oluşturma:** Araç detay sayfasından erişilen form ve görünüm (`reservation_create`) (Tarih seçimi, çakışma kontrolü, fiyat hesaplama).
-   **Kullanıcı Paneli (Dashboard) Üzerinden Rezervasyon Yönetimi:** Tüm rezervasyonlar (aktif ve geçmiş) kullanıcı panelinde (dashboard) 5'erli sayfalama (pagination) ile listelenir ve yönetilir. Ayrı bir "Rezervasyonlarım" (my_reservations) sayfası ve fonksiyonu kaldırılmıştır. Kod ve şablonlar sadeleştirilmiştir.
-   **Rezervasyon İptali:** Aktif rezervasyonlar için iptal fonksiyonu (`reservation_cancel`).
-   **Rezervasyon Onay/Red Akışı:** Yeni rezervasyonlar "Beklemede" (pending) başlar, admin panelinden onaylanabilir veya reddedilebilir. Kullanıcıya rezervasyon durumu hakkında bilgilendirme yapılır.
-   `Reservation` modeli veritabanında rezervasyon bilgilerini tutar.
-   `_reservation_table.html` partial template'i ile rezervasyon listesi tutarlı şekilde gösterilir (dashboard'da sayfalama ile).
-   Araç müsait olmayan tarihler için API endpoint'i (`car_unavailable_dates`).

### 5. Kullanıcı Profili (`rentals`)
-   Giriş yapmış kullanıcılara özel profil sayfası (`profile_view`).
-   Kişisel bilgilerin (Ad, Soyad, E-posta) görüntülenmesi ve güncellenmesi.
-   **Gelişmiş Profil Alanları:** Kullanıcı profiline adres, telefon, ehliyet bilgisi, doğum tarihi ve profil fotoğrafı eklenmiştir. Kullanıcılar bu bilgileri güncelleyebilir.
-   **"Ayarlar ve Tercihler" Bölümü:** Gelecekteki ayarlar için yer tutucu.

### 6. Diğer Sayfalar (`core`)
-   **Hakkımızda:** Statik içerik sayfası (`about_view`).
-   **İletişim:** İletişim formu ve mesaj kaydetme (`contact_view`).

### 7. Admin Paneli
-   Django admin paneli aktif.
-   Rezervasyonlar için özel filtreler ve toplu işlemler eklenmiş.
-   **Araç ve Rezervasyon Durum Yönetimi:** Admin panelinden araçların durumu (müsait, bakımda, kirada) ve rezervasyonların durumu (beklemede, onaylandı, reddedildi, iptal edildi, tamamlandı) kolayca yönetilebilir.

### 8. Teknolojiler ve Frontend
-   Django (Backend)
-   Bootstrap 5 (Frontend Framework)
-   Özel CSS (`custom.css`)
-   JavaScript (Bootstrap, AOS, vb.)
-   HTML5 / CSS3
-   SQLite (Geliştirme veritabanı)

## Özet
Proje, kullanıcıların kayıt/giriş yapabildiği, araçları listeleyip detaylarını görebildiği, rezervasyon yapıp yönetebildiği ve profillerini güncelleyebildiği modern görünümlü bir araç kiralama platformunun temel işlevlerini içerir. Anasayfa ve genel tasarım, markanın modern kimliğini yansıtacak şekilde geliştirilmiştir. 

## Ek Geliştirmeler ve Mimari İyileştirmeler
-   Kodun tamamında tekil durum yönetimi (status alanı) ile veri tutarlılığı ve bakım kolaylığı sağlandı. Ayrıca, rezervasyon yönetimi dashboard üzerinden merkezi ve sade bir yapıya kavuşturuldu.
-   Araçlar sadece bakımda ise listelenmez; kirada olsa bile farklı tarihler için kiralanabilir.
-   Müsaitlik kontrolü, rezervasyon çakışması ile sağlanır; araçlar bakımda değilse her zaman listelenir. 