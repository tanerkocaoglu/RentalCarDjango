from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login
from django.contrib import messages
from datetime import datetime, timedelta
from decimal import Decimal
from django.db import models # models import edildi
from .models import Car, Reservation, UserProfile
from django.http import HttpResponseForbidden, JsonResponse
from .forms import UserProfileForm, UserBasicForm
from django.views.decorators.http import require_http_methods
from django.core.cache import cache

def home_view(request):
    """Basit anasayfa view'ı. Popüler araçları da gönderir."""
    from .models import Car
    popular_cars = cache.get('popular_cars')
    if not popular_cars:
        popular_cars = Car.objects.filter(status='available').select_related().order_by('-year', '-id')[:3]
        cache.set('popular_cars', popular_cars, 600)  # 600 saniye = 10 dakika
    return render(request, 'rentals/home.html', {'popular_cars': popular_cars})

def car_list(request):
    """
    Araçları listeleyen, arama ve filtreleme yapan view.
    """
    # Filtre parametrelerini al
    search_query = request.GET.get('search', '')
    brand_filter = request.GET.get('brand', '')
    year_filter = request.GET.get('year', '')
    min_price = request.GET.get('min_price', '')
    max_price = request.GET.get('max_price', '')
    availability = request.GET.get('availability', 'available')

    # Cache anahtarı oluştur
    cache_key = f"car_list_{search_query}_{brand_filter}_{year_filter}_{min_price}_{max_price}_{availability}"
    cars = cache.get(cache_key)
    if not cars:
        # Varsayılan olarak sadece müsait araçları göster (bakımda olanlar hariç)
        cars = Car.objects.filter(status='available').select_related()
        # Arama filtrelerini uygula
        if search_query:
            cars = cars.filter(
                models.Q(brand__icontains=search_query) |
                models.Q(model__icontains=search_query) |
                models.Q(description__icontains=search_query)
            )
        if brand_filter:
            cars = cars.filter(brand__iexact=brand_filter)
        if year_filter:
            cars = cars.filter(year=year_filter)
        if min_price:
            cars = cars.filter(daily_rate__gte=min_price)
        if max_price:
            cars = cars.filter(daily_rate__lte=max_price)
        if availability == 'all':
            cars = Car.objects.exclude(status='maintenance').select_related()
        elif availability == 'unavailable':
            cars = Car.objects.filter(status='maintenance').select_related()
        # Sonuçları cache'e yaz
        cache.set(cache_key, cars, 600)

    # Mevcut tüm marka ve yılları al (filtreleme seçenekleri için)
    all_brands = Car.objects.values_list('brand', flat=True).distinct().order_by('brand')
    all_years = Car.objects.values_list('year', flat=True).distinct().order_by('-year')

    context = {
        'cars': cars,
        'all_brands': all_brands,
        'all_years': all_years,
        'search_query': search_query,
        'brand_filter': brand_filter,
        'year_filter': year_filter,
        'min_price': min_price,
        'max_price': max_price,
        'availability': availability,
    }
    return render(request, 'rentals/car_list.html', context)

def car_detail(request, pk):
    """
    Belirli bir aracın detaylarını gösteren view.
    """
    car = get_object_or_404(Car, pk=pk)
    context = {
        'car': car,
    }
    return render(request, 'rentals/car_detail.html', context)

@login_required
def reservation_create(request, car_id):
    """
    Araç rezervasyonu oluşturma view'ı.
    Sadece giriş yapmış kullanıcılar erişebilir.
    """
    car = get_object_or_404(Car, pk=car_id)
    
    if request.method == 'POST':
        # Form verilerini al
        start_date = datetime.strptime(request.POST['start_date'], '%Y-%m-%d').date()
        end_date = datetime.strptime(request.POST['end_date'], '%Y-%m-%d').date()
        
        # Tarih kontrolü
        if start_date < datetime.now().date():
            messages.error(request, 'Geçmiş bir tarih seçemezsiniz.')
            return redirect('rentals:car_detail', pk=car_id)
        
        if end_date < start_date:
            messages.error(request, 'Bitiş tarihi başlangıç tarihinden önce olamaz.')
            return redirect('rentals:car_detail', pk=car_id)
        
        # Tarih aralığında başka rezervasyon var mı kontrol et
        conflicting_reservations = Reservation.objects.filter(
            car=car,
            start_date__lte=end_date,
            end_date__gte=start_date,
            status='confirmed'
        )
        
        if conflicting_reservations.exists():
            messages.error(request, 'Seçtiğiniz tarihler için araç müsait değil.')
            return redirect('rentals:car_detail', pk=car_id)
        
        # Toplam gün sayısı ve fiyat hesaplama
        days = (end_date - start_date).days + 1
        total_price = car.daily_rate * Decimal(days)
        
        # Rezervasyon oluştur (artık pending başlasın)
        reservation = Reservation.objects.create(
            user=request.user,
            car=car,
            start_date=start_date,
            end_date=end_date,
            total_price=total_price,
            status='pending'  # Artık beklemede başlıyor
        )
        
        messages.info(request, 'Rezervasyonunuz alınmıştır, yönetici onayını bekliyor.')
        return redirect('rentals:my_reservations')
    
    context = {
        'car': car,
        'min_date': datetime.now().date().strftime('%Y-%m-%d'),
        'max_date': (datetime.now().date() + timedelta(days=90)).strftime('%Y-%m-%d'),  # 90 gün ileri
    }
    return render(request, 'rentals/reservation_form.html', context)

@login_required
def my_reservations(request):
    """
    Kullanıcının kendi rezervasyonlarını görüntüleme view'ı.
    Duruma göre filtreleme yapar.
    """
    status_filter = request.GET.get('status', 'active') # Varsayılan: aktif
    user_id = request.user.id
    cache_key = f"my_reservations_{user_id}_{status_filter}"
    reservations = cache.get(cache_key)
    if not reservations:
        reservations = Reservation.objects.filter(user=request.user).select_related('car')
        if status_filter == 'active':
            reservations = reservations.filter(status__in=['confirmed', 'pending'])
        elif status_filter == 'completed':
            reservations = reservations.filter(status='completed')
        elif status_filter == 'cancelled':
            reservations = reservations.filter(status='cancelled')
        elif status_filter != 'all':
            status_filter = 'active'
            reservations = reservations.filter(status__in=['confirmed', 'pending'])
        reservations = reservations.order_by('-created_at')
        cache.set(cache_key, reservations, 600)
    context = {
        'reservations': reservations,
        'status_filter': status_filter, # Seçili filtreyi template'e gönder
    }
    return render(request, 'rentals/my_reservations.html', context)

@login_required
def reservation_cancel(request, reservation_id):
    """
    Kullanıcıya ait bir rezervasyonu iptal eder ve aracı tekrar müsait yapar.
    Sadece rezervasyonun sahibi erişebilir. GET ile erişimde onay sayfası gösterilir, POST ile iptal edilir.
    """
    reservation = get_object_or_404(Reservation, id=reservation_id)
    if reservation.user != request.user:
        return HttpResponseForbidden("Bu rezervasyonu iptal etme yetkiniz yok.")
    if reservation.status == 'cancelled':
        messages.info(request, 'Bu rezervasyon zaten iptal edilmiş.')
        return redirect('rentals:my_reservations')
    if request.method == 'POST':
        reservation.status = 'cancelled'
        reservation.save()
        messages.success(request, 'Rezervasyon başarıyla iptal edildi.')
        return redirect('rentals:my_reservations')
    # GET ise onay sayfası göster
    return render(request, 'rentals/reservation_confirm_cancel.html', {'reservation': reservation})

def signup(request):
    """
    Yeni kullanıcı kaydı oluşturma view'ı
    """
    if request.user.is_authenticated:
        messages.info(request, 'Zaten giriş yapmış durumdasınız.')
        return redirect('rentals:car_list')
        
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)  # Kullanıcıyı otomatik olarak giriş yaptır
            messages.success(request, 'Hesabınız başarıyla oluşturuldu!')
            return redirect('rentals:car_list')
    else:
        form = UserCreationForm()
    
    return render(request, 'registration/signup.html', {
        'form': form,
        'title': 'Kayıt Ol'
    })

@login_required
def profile_view(request):
    user = request.user
    # UserProfile nesnesi yoksa oluştur
    profile, created = UserProfile.objects.get_or_create(user=user)

    if request.method == 'POST':
        user_form = UserBasicForm(request.POST, instance=user)
        profile_form = UserProfileForm(request.POST, request.FILES, instance=profile)
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(request, 'Profil bilgileriniz güncellendi.')
            return redirect('rentals:profile')
    else:
        user_form = UserBasicForm(instance=user)
        profile_form = UserProfileForm(instance=profile)
    # Kullanıcının tüm rezervasyonları
    reservations = user.reservation_set.all().order_by('-created_at')
    context = {
        'user_form': user_form,
        'profile_form': profile_form,
        'reservations': reservations,
    }
    return render(request, 'rentals/profile.html', context)

def car_unavailable_dates(request, car_id):
    """
    Seçilen araca ait tüm onaylanmış rezervasyonların günlerini JSON olarak döner.
    """
    reservations = Reservation.objects.filter(
        car_id=car_id,
        status='confirmed'
    )
    unavailable = set()
    for r in reservations:
        current = r.start_date
        while current <= r.end_date:
            unavailable.add(current.strftime('%Y-%m-%d'))
            current += timedelta(days=1)
    return JsonResponse({'unavailable_dates': sorted(unavailable)})

def about_view(request):
    return render(request, 'rentals/about.html')

def contact_view(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        message = request.POST.get('message')
        ContactMessage.objects.create(name=name, email=email, message=message)
        messages.success(request, 'Mesajınız başarıyla gönderildi! En kısa sürede sizinle iletişime geçeceğiz.')
        return redirect('rentals:contact')
    return render(request, 'rentals/contact.html')

@login_required
def dashboard_view(request):
    user = request.user
    profile, _ = UserProfile.objects.get_or_create(user=user)
    # Aktif rezervasyonlar: onaylı veya beklemede
    active_reservations = Reservation.objects.filter(user=user, status__in=['confirmed', 'pending']).select_related('car').order_by('-start_date')
    # Geçmiş rezervasyonlar: tamamlanmış, iptal edilmiş veya reddedilmiş
    past_reservations = Reservation.objects.filter(user=user, status__in=['completed', 'cancelled', 'rejected']).select_related('car').order_by('-start_date')
    context = {
        'profile': profile,
        'active_reservations': active_reservations,
        'past_reservations': past_reservations,
    }
    return render(request, 'rentals/dashboard.html', context)
