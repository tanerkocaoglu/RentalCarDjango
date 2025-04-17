from django.db import models
from django.contrib.auth.models import User # Kullanıcı modelini import ediyoruz
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.core.cache import cache

# Create your models here.

class Car(models.Model):
    STATUS_CHOICES = [
        ('available', 'Müsait'),
        ('rented', 'Kirada'),
        ('maintenance', 'Bakımda'),
    ]
    brand = models.CharField(max_length=100, verbose_name="Marka")
    model = models.CharField(max_length=100, verbose_name="Model")
    year = models.IntegerField(verbose_name="Yıl")
    license_plate = models.CharField(max_length=20, unique=True, verbose_name="Plaka")
    daily_rate = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Günlük Fiyat")
    description = models.TextField(blank=True, verbose_name="Açıklama")
    image = models.ImageField(upload_to='cars/', blank=True, null=True, verbose_name="Araç Resmi") # upload_to belirtildi
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='available', verbose_name="Durum")

    def __str__(self):
        return f"{self.year} {self.brand} {self.model} ({self.license_plate})"

    class Meta:
        verbose_name = "Araç"
        verbose_name_plural = "Araçlar"
        ordering = ['brand', 'model'] # Sıralama eklendi

@receiver(post_save, sender=Car)
def clear_car_list_cache_on_save(sender, instance, **kwargs):
    # Tüm olası filtre kombinasyonları için cache anahtarlarını temizlemek için basit bir yaklaşım
    # (Daha gelişmiş bir sistemde, cache anahtarları merkezi bir yerde tutulabilir)
    cache.delete('popular_cars')
    # Sık kullanılan bazı filtre kombinasyonlarını temizle
    for availability in ['available', 'unavailable', 'all']:
        for brand in ['', instance.brand]:
            for year in ['', str(instance.year)]:
                cache_key = f"car_list__{brand}_{year}___{availability}"
                cache.delete(cache_key)
    # Not: Eğer çok fazla kombinasyon varsa, cache.clear() ile tüm cache silinebilir (küçük projelerde uygundur)

@receiver(post_delete, sender=Car)
def clear_car_list_cache_on_delete(sender, instance, **kwargs):
    cache.delete('popular_cars')
    for availability in ['available', 'unavailable', 'all']:
        for brand in ['', instance.brand]:
            for year in ['', str(instance.year)]:
                cache_key = f"car_list__{brand}_{year}___{availability}"
                cache.delete(cache_key)

class Reservation(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Bekliyor'),
        ('confirmed', 'Onaylandı'),
        ('cancelled', 'İptal Edildi'),
        ('rejected', 'Reddedildi'),
        ('completed', 'Tamamlandı'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Kullanıcı")
    car = models.ForeignKey(Car, on_delete=models.CASCADE, verbose_name="Araç")
    start_date = models.DateField(verbose_name="Başlangıç Tarihi")
    end_date = models.DateField(verbose_name="Bitiş Tarihi")
    total_price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Toplam Fiyat") # Hesaplanacak veya girilecek
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending', verbose_name="Durum")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Oluşturulma Tarihi") # Ekstra bilgi

    def __str__(self):
        return f"{self.user.username} - {self.car.brand} {self.car.model} ({self.start_date} - {self.end_date})"

    class Meta:
        verbose_name = "Rezervasyon"
        verbose_name_plural = "Rezervasyonlar"
        ordering = ['-created_at'] # En yeni rezervasyonlar üstte

    # İsteğe bağlı: Toplam fiyatı otomatik hesaplama metodu eklenebilir
    # def save(self, *args, **kwargs):
    #     if not self.total_price:
    #         duration = (self.end_date - self.start_date).days + 1
    #         self.total_price = duration * self.car.daily_rate
    #     super().save(*args, **kwargs)

@receiver(post_save, sender=Reservation)
def clear_dashboard_reservations_cache_on_save(sender, instance, **kwargs):
    # Dashboard'daki rezervasyon cache'ini temizle
    user_id = instance.user.id
    cache.delete(f"dashboard_active_reservations_{user_id}")
    cache.delete(f"dashboard_past_reservations_{user_id}")

@receiver(post_delete, sender=Reservation)
def clear_dashboard_reservations_cache_on_delete(sender, instance, **kwargs):
    # Dashboard'daki rezervasyon cache'ini temizle
    user_id = instance.user.id
    cache.delete(f"dashboard_active_reservations_{user_id}")
    cache.delete(f"dashboard_past_reservations_{user_id}")

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile', verbose_name="Kullanıcı")
    address = models.CharField(max_length=255, blank=True, verbose_name="Adres")
    phone = models.CharField(max_length=20, blank=True, verbose_name="Telefon")
    driver_license = models.CharField(max_length=50, blank=True, verbose_name="Ehliyet Bilgisi")
    birth_date = models.DateField(null=True, blank=True, verbose_name="Doğum Tarihi")
    profile_image = models.ImageField(upload_to='profiles/', blank=True, null=True, verbose_name="Profil Fotoğrafı")

    def __str__(self):
        return f"{self.user.username} Profili"

    class Meta:
        verbose_name = "Kullanıcı Profili"
        verbose_name_plural = "Kullanıcı Profilleri"
