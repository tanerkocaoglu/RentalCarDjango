from django.test import TestCase, Client
from django.urls import reverse
from .models import Car, Reservation
from django.contrib.auth.models import User
from decimal import Decimal
from datetime import date

# Create your tests here.

class CarModelTest(TestCase):

    @classmethod
    def setUpTestData(cls):
        # Test veritabanına bir kerelik örnek bir Car nesnesi oluştur
        # Bu, her test metodu için tekrar tekrar oluşturulmaz, daha verimlidir.
        Car.objects.create(
            brand="TestMarka",
            model="TestModel",
            year=2024,
            license_plate="34TEST34",
            daily_rate=Decimal("100.50"),
            description="Test açıklaması"
        )

    def test_car_creation(self):
        """Car nesnesinin doğru oluşturulduğunu ve alanların doğru atandığını test eder."""
        car = Car.objects.get(license_plate="34TEST34")
        self.assertEqual(car.brand, "TestMarka")
        self.assertEqual(car.model, "TestModel")
        self.assertEqual(car.year, 2024)
        self.assertEqual(car.daily_rate, Decimal("100.50"))
        self.assertEqual(car.status, 'available')

    def test_car_str_representation(self):
        """Car modelinin __str__ metodunun doğru formatta string döndürdüğünü test eder."""
        car = Car.objects.get(license_plate="34TEST34")
        expected_str = f"{car.year} {car.brand} {car.model} ({car.license_plate})"
        self.assertEqual(str(car), expected_str)

class ReservationModelTest(TestCase):

    @classmethod
    def setUpTestData(cls):
        # Rezervasyon için gerekli User ve Car nesnelerini oluştur
        cls.user = User.objects.create_user(username='testuser', password='password123')
        cls.car = Car.objects.create(
            brand="TestMarka",
            model="TestModel",
            year=2024,
            license_plate="34TEST34",
            daily_rate=Decimal("100.00")
        )
        # Örnek bir Reservation nesnesi oluştur
        cls.reservation = Reservation.objects.create(
            user=cls.user,
            car=cls.car,
            start_date=date(2025, 5, 1),
            end_date=date(2025, 5, 5),
            total_price=Decimal("500.00"), # 5 gün * 100.00
            # status varsayılan 'pending' olacak
        )

    def test_reservation_creation(self):
        """Reservation nesnesinin doğru oluşturulduğunu ve alanların doğru atandığını test eder."""
        res = Reservation.objects.get(id=self.reservation.id)
        self.assertEqual(res.user, self.user)
        self.assertEqual(res.car, self.car)
        self.assertEqual(res.start_date, date(2025, 5, 1))
        self.assertEqual(res.end_date, date(2025, 5, 5))
        self.assertEqual(res.total_price, Decimal("500.00"))
        self.assertEqual(res.status, 'pending') # Varsayılan durumun pending olduğunu kontrol et

    def test_reservation_str_representation(self):
        """Reservation modelinin __str__ metodunun doğru formatta string döndürdüğünü test eder."""
        res = Reservation.objects.get(id=self.reservation.id)
        expected_str = f"{res.user.username} - {res.car.brand} {res.car.model} ({res.start_date} - {res.end_date})"
        self.assertEqual(str(res), expected_str)

class RentalViewsTest(TestCase):

    @classmethod
    def setUpTestData(cls):
        # View testleri için gerekli Car ve User nesnelerini oluştur
        cls.test_user = User.objects.create_user(username='viewtestuser', password='password123')
        cls.car = Car.objects.create(
            brand="ViewTestMarka",
            model="ViewTestModel",
            year=2023,
            license_plate="34VIEW34",
            daily_rate=Decimal("150.00")
        )
        cls.client = Client() # Test istemcisini oluştur

    def test_car_list_view(self):
        """car_list view'ının durum kodunu ve kullanılan şablonu test eder."""
        response = self.client.get(reverse('rentals:car_list')) # Ana URL'i (car_list) al
        self.assertEqual(response.status_code, 200) # Başarılı yanıt (200 OK) kontrolü
        self.assertTemplateUsed(response, 'rentals/car_list.html') # Doğru şablon kullanıldı mı?

    def test_car_detail_view_success(self):
        """car_detail view'ının geçerli bir araç için durum kodunu ve şablonunu test eder."""
        url = reverse('rentals:car_detail', args=[self.car.pk]) # Geçerli araç ID'si ile URL al
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'rentals/car_detail.html')
        self.assertContains(response, self.car.brand) # Sayfa içeriğinde araç markası var mı?

    def test_car_detail_view_not_found(self):
        """car_detail view'ının geçersiz bir araç ID'si için 404 döndürdüğünü test eder."""
        invalid_pk = self.car.pk + 999 # Var olmayan bir ID
        url = reverse('rentals:car_detail', args=[invalid_pk])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404) # 404 Not Found kontrolü

    # def test_my_reservations_view_redirects_if_not_logged_in(self):
    #     """my_reservations view'ına giriş yapmadan erişildiğinde login sayfasına yönlendirir."""
    #     response = self.client.get(reverse('rentals:my_reservations'))
    #     login_url = reverse('login')
    #     target_url = reverse('rentals:my_reservations')
    #     self.assertRedirects(response, f'{login_url}?next={target_url}')

    # def test_my_reservations_view_accessible_if_logged_in(self):
    #     """my_reservations view'ına giriş yapıldıktan sonra erişilebilir."""
    #     self.client.login(username='viewtestuser', password='password123')
    #     response = self.client.get(reverse('rentals:my_reservations'))
    #     self.assertEqual(response.status_code, 200)
    #     self.assertTemplateUsed(response, 'rentals/my_reservations.html')
    #     self.client.logout()

    def test_profile_view_redirects_if_not_logged_in(self):
        """profile_view'a giriş yapmadan erişildiğinde login sayfasına yönlendirir."""
        response = self.client.get(reverse('rentals:profile'))
        login_url = reverse('login')
        target_url = reverse('rentals:profile')
        self.assertRedirects(response, f'{login_url}?next={target_url}')

    def test_profile_view_accessible_if_logged_in(self):
        """profile_view'a giriş yapıldıktan sonra erişilebilir."""
        self.client.login(username='viewtestuser', password='password123')
        response = self.client.get(reverse('rentals:profile'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'rentals/profile.html')
        self.client.logout() # Test sonrası çıkış yap

    def test_reservation_create_redirects_if_not_logged_in(self):
        """Giriş yapmadan reservation_create view'ına erişim login'e yönlendirir."""
        response = self.client.get(reverse('rentals:reservation_create', args=[self.car.pk]))
        login_url = reverse('login')
        target_url = reverse('rentals:reservation_create', args=[self.car.pk])
        self.assertRedirects(response, f'{login_url}?next={target_url}')

    def test_reservation_create_get_form_if_logged_in(self):
        """Giriş yaptıktan sonra reservation_create view'ı GET ile formu döndürür."""
        self.client.login(username='viewtestuser', password='password123')
        response = self.client.get(reverse('rentals:reservation_create', args=[self.car.pk]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'rentals/reservation_form.html')
        self.client.logout()

    def test_reservation_create_post_valid(self):
        """Geçerli POST ile rezervasyon oluşturulur ve yönlendirilir."""
        self.client.login(username='viewtestuser', password='password123')
        post_data = {
            'start_date': date(2025, 6, 1),
            'end_date': date(2025, 6, 3),
        }
        response = self.client.post(
            reverse('rentals:reservation_create', args=[self.car.pk]),
            post_data
        )
        # Başarılı rezervasyon sonrası yönlendirme beklenir (ör: my_reservations)
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Reservation.objects.filter(user__username='viewtestuser', car=self.car, start_date=date(2025, 6, 1)).exists())
        self.client.logout()

    def test_reservation_create_post_invalid(self):
        """Geçersiz POST ile form tekrar gösterilir ve hata mesajı içerir."""
        self.client.login(username='viewtestuser', password='password123')
        post_data = {
            'start_date': '',  # Eksik veri
            'end_date': '',
        }
        response = self.client.post(
            reverse('rentals:reservation_create', args=[self.car.pk]),
            post_data
        )
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'rentals/reservation_form.html')
        self.assertContains(response, 'Bu alan zorunludur')

    def test_register_view_get(self):
        """register view'ı GET ile formu döndürür."""
        response = self.client.get(reverse('rentals:register'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'registration/register.html')

    def test_register_view_post_valid(self):
        """Geçerli POST ile yeni kullanıcı oluşturulur ve yönlendirilir."""
        post_data = {
            'username': 'newuser',
            'password1': 'strongpassword123',
            'password2': 'strongpassword123',
        }
        response = self.client.post(reverse('rentals:register'), post_data)
        # Başarılı kayıt sonrası yönlendirme beklenir (ör: login sayfası)
        self.assertEqual(response.status_code, 302)
        self.assertTrue(User.objects.filter(username='newuser').exists())

    def test_register_view_post_invalid(self):
        """Geçersiz POST ile form tekrar gösterilir ve hata mesajı içerir."""
        post_data = {
            'username': '',  # Eksik kullanıcı adı
            'password1': 'pw',
            'password2': 'pw',
        }
        response = self.client.post(reverse('rentals:register'), post_data)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'registration/register.html')
        self.assertContains(response, 'Bu alan zorunludur')

    def test_car_list_filter_by_brand(self):
        """car_list view'ı marka filtresiyle doğru arabaları listeler."""
        # Farklı marka bir araç ekle
        Car.objects.create(
            brand="FiltreMarka",
            model="ModelX",
            year=2022,
            license_plate="34FILTRE01",
            daily_rate=Decimal("120.00")
        )
        response = self.client.get(reverse('rentals:car_list') + '?brand=FiltreMarka')
        self.assertContains(response, 'FiltreMarka')
        self.assertNotContains(response, 'ViewTestMarka')

    def test_car_list_filter_by_model(self):
        """car_list view'ı model filtresiyle doğru arabaları listeler."""
        Car.objects.create(
            brand="TestBrand",
            model="FiltreModel",
            year=2021,
            license_plate="34FILTRE02",
            daily_rate=Decimal("110.00")
        )
        response = self.client.get(reverse('rentals:car_list') + '?model=FiltreModel')
        self.assertContains(response, 'FiltreModel')
        self.assertNotContains(response, 'ViewTestModel')

    def test_password_change_redirects_if_not_logged_in(self):
        """Giriş yapmadan password_change view'ına erişim login'e yönlendirir."""
        response = self.client.get(reverse('password_change'))
        login_url = reverse('login')
        target_url = reverse('password_change')
        self.assertRedirects(response, f'{login_url}?next={target_url}')

    def test_password_change_get_form_if_logged_in(self):
        """Giriş yaptıktan sonra password_change view'ı GET ile formu döndürür."""
        self.client.login(username='viewtestuser', password='password123')
        response = self.client.get(reverse('password_change'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'registration/password_change_form.html')
        self.client.logout()

    def test_password_change_post_valid(self):
        """Geçerli POST ile şifre değişir ve yönlendirme olur."""
        self.client.login(username='viewtestuser', password='password123')
        post_data = {
            'old_password': 'password123',
            'new_password1': 'yeniSifre12345',
            'new_password2': 'yeniSifre12345',
        }
        response = self.client.post(reverse('password_change'), post_data)
        # Başarılı değişiklik sonrası yönlendirme (default: password_change_done)
        self.assertRedirects(response, reverse('password_change_done'))
        self.client.logout()
        # Yeni şifreyle giriş yapılabiliyor mu?
        login = self.client.login(username='viewtestuser', password='yeniSifre12345')
        self.assertTrue(login)

    def test_password_change_post_invalid(self):
        """Geçersiz POST ile form tekrar gösterilir ve hata mesajı içerir."""
        self.client.login(username='viewtestuser', password='password123')
        post_data = {
            'old_password': 'yanlisSifre',
            'new_password1': 'short',
            'new_password2': 'short',
        }
        response = self.client.post(reverse('password_change'), post_data)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'registration/password_change_form.html')
        self.assertContains(response, 'Şifre')  # Hata mesajı içermeli
        self.client.logout()

    def test_password_reset_get_form(self):
        """password_reset view'ı GET ile formu döndürür."""
        response = self.client.get(reverse('password_reset'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'registration/password_reset_form.html')

    def test_password_reset_post_valid_email(self):
        """Kayıtlı e-posta ile POST yapıldığında yönlendirme ve e-posta gönderimi olur."""
        user_email = 'viewtestuser@example.com'
        self.test_user.email = user_email
        self.test_user.save()
        post_data = {'email': user_email}
        response = self.client.post(reverse('password_reset'), post_data)
        self.assertRedirects(response, reverse('password_reset_done'))
        # Django test framework'ü gönderilen e-postaları outbox'ta tutar
        from django.core import mail
        self.assertEqual(len(mail.outbox), 1)
        self.assertIn(user_email, mail.outbox[0].to)

    def test_password_reset_post_invalid_email(self):
        """Kayıtlı olmayan e-posta ile POST yapıldığında yönlendirme olur ama e-posta gönderilmez."""
        post_data = {'email': 'olmayan@example.com'}
        response = self.client.post(reverse('password_reset'), post_data)
        self.assertRedirects(response, reverse('password_reset_done'))
        from django.core import mail
        self.assertEqual(len(mail.outbox), 0)

    def test_profile_update_redirects_if_not_logged_in(self):
        """Giriş yapmadan profile_update view'ına erişim login'e yönlendirir."""
        response = self.client.get(reverse('rentals:profile_update'))
        login_url = reverse('login')
        target_url = reverse('rentals:profile_update')
        self.assertRedirects(response, f'{login_url}?next={target_url}')

    def test_profile_update_get_form_if_logged_in(self):
        """Giriş yaptıktan sonra profile_update view'ı GET ile formu döndürür."""
        self.client.login(username='viewtestuser', password='password123')
        response = self.client.get(reverse('rentals:profile_update'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'rentals/profile_form.html')
        self.client.logout()

    def test_profile_update_post_valid(self):
        """Geçerli POST ile profil güncellenir ve yönlendirme olur."""
        self.client.login(username='viewtestuser', password='password123')
        post_data = {
            'first_name': 'YeniAd',
            'last_name': 'YeniSoyad',
            'email': 'yeniemail@example.com',
        }
        response = self.client.post(reverse('rentals:profile_update'), post_data)
        self.assertEqual(response.status_code, 302)
        self.test_user.refresh_from_db()
        self.assertEqual(self.test_user.first_name, 'YeniAd')
        self.assertEqual(self.test_user.last_name, 'YeniSoyad')
        self.assertEqual(self.test_user.email, 'yeniemail@example.com')
        self.client.logout()

    def test_profile_update_post_invalid(self):
        """Geçersiz POST ile form tekrar gösterilir ve hata mesajı içerir."""
        self.client.login(username='viewtestuser', password='password123')
        post_data = {
            'first_name': '',  # Zorunlu alanı boş bırak
            'last_name': '',
            'email': 'gecersizemail',  # Geçersiz e-posta
        }
        response = self.client.post(reverse('rentals:profile_update'), post_data)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'rentals/profile_form.html')
        self.assertContains(response, 'Bu alan zorunludur')
        self.client.logout()

    def test_reservation_cancel_redirects_if_not_logged_in(self):
        """Giriş yapmadan reservation_cancel view'ına erişim login'e yönlendirir."""
        # Önce bir rezervasyon oluştur
        reservation = Reservation.objects.create(
            user=self.test_user,
            car=self.car,
            start_date=date(2025, 7, 1),
            end_date=date(2025, 7, 3),
            total_price=Decimal("300.00")
        )
        response = self.client.get(reverse('rentals:reservation_cancel', args=[reservation.pk]))
        login_url = reverse('login')
        target_url = reverse('rentals:reservation_cancel', args=[reservation.pk])
        self.assertRedirects(response, f'{login_url}?next={target_url}')

    def test_reservation_cancel_get_form_if_logged_in(self):
        """Giriş yaptıktan sonra reservation_cancel view'ı GET ile onay formunu döndürür."""
        reservation = Reservation.objects.create(
            user=self.test_user,
            car=self.car,
            start_date=date(2025, 7, 4),
            end_date=date(2025, 7, 6),
            total_price=Decimal("300.00")
        )
        self.client.login(username='viewtestuser', password='password123')
        response = self.client.get(reverse('rentals:reservation_cancel', args=[reservation.pk]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'rentals/reservation_confirm_cancel.html')
        self.client.logout()

    def test_reservation_cancel_post_valid(self):
        """Giriş yaptıktan sonra POST ile rezervasyon iptal edilir ve yönlendirme olur."""
        reservation = Reservation.objects.create(
            user=self.test_user,
            car=self.car,
            start_date=date(2025, 7, 7),
            end_date=date(2025, 7, 9),
            total_price=Decimal("300.00")
        )
        self.client.login(username='viewtestuser', password='password123')
        response = self.client.post(reverse('rentals:reservation_cancel', args=[reservation.pk]))
        self.assertEqual(response.status_code, 302)
        # Rezervasyonun silindiğini veya iptal edildiğini kontrol et
        exists = Reservation.objects.filter(pk=reservation.pk).exists()
        self.assertFalse(exists)
        self.client.logout()

    def test_reservation_cancel_other_user_forbidden(self):
        """Başka kullanıcıya ait rezervasyonu iptal etmeye çalışınca erişim engellenir."""
        other_user = User.objects.create_user(username='otheruser', password='otherpass')
        reservation = Reservation.objects.create(
            user=other_user,
            car=self.car,
            start_date=date(2025, 7, 10),
            end_date=date(2025, 7, 12),
            total_price=Decimal("300.00")
        )
        self.client.login(username='viewtestuser', password='password123')
        response = self.client.get(reverse('rentals:reservation_cancel', args=[reservation.pk]))
        # 403 Forbidden veya başka bir erişim engeli beklenir
        self.assertIn(response.status_code, [403, 302])
        self.client.logout()
