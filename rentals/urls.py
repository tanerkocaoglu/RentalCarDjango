from django.urls import path
from . import views

app_name = 'rentals'

urlpatterns = [
    # Araç listesi sayfası
    path('araclar/', views.car_list, name='car_list'),
    # Araç detay sayfası (URL'den aracın ID'sini alır)
    path('car/<int:pk>/', views.car_detail, name='car_detail'),
    # Rezervasyon işlemleri
    path('car/<int:car_id>/reserve/', views.reservation_create, name='reservation_create'),
    path('reservation/<int:reservation_id>/cancel/', views.reservation_cancel, name='reservation_cancel'),
    # Kullanıcı işlemleri
    path('profile/', views.profile_view, name='profile'),
    path('dashboard/', views.dashboard_view, name='dashboard'),
    path('car/<int:car_id>/unavailable-dates/', views.car_unavailable_dates, name='car_unavailable_dates'),
    path('hakkimizda/', views.about_view, name='about'),
    path('iletisim/', views.contact_view, name='contact'),
]