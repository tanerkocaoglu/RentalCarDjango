from django.contrib import admin
from .models import Car, Reservation, UserProfile
from datetime import date

class ActiveReservationFilter(admin.SimpleListFilter):
    title = 'Aktiflik'
    parameter_name = 'active_status'

    def lookups(self, request, model_admin):
        return (
            ('active', 'Aktif Rezervasyonlar'),
            ('all', 'Tüm Rezervasyonlar'),
        )

    def queryset(self, request, queryset):
        if self.value() == 'active':
            return queryset.filter(status='confirmed', end_date__gte=date.today())
        return queryset

@admin.register(Car)
class CarAdmin(admin.ModelAdmin):
    list_display = ('brand', 'model', 'year', 'license_plate', 'daily_rate', 'status')
    list_filter = ('brand', 'year', 'status')
    search_fields = ('brand', 'model', 'license_plate')
    list_editable = ('status',)
    actions = ['make_available', 'make_unavailable']
    
    def make_available(self, request, queryset):
        updated = queryset.update(status='available')
        self.message_user(request, f'{updated} adet araç müsait duruma getirildi.')
    make_available.short_description = "Seçili araçları müsait duruma getir"
    
    def make_unavailable(self, request, queryset):
        updated = queryset.update(status='maintenance')
        self.message_user(request, f'{updated} adet araç bakımda/kapalı duruma getirildi.')
    make_unavailable.short_description = "Seçili araçları bakımda/kapalı duruma getir"

@admin.register(Reservation)
class ReservationAdmin(admin.ModelAdmin):
    list_display = ('user', 'car', 'start_date', 'end_date', 'total_price', 'status', 'created_at')
    list_filter = (ActiveReservationFilter, 'status', 'start_date', 'created_at')
    search_fields = ('user__username', 'car__license_plate')
    readonly_fields = ('created_at',)
    actions = ['mark_as_cancelled', 'mark_as_confirmed', 'mark_as_completed', 'mark_as_rejected']
    
    def mark_as_cancelled(self, request, queryset):
        updated = queryset.update(status='cancelled')
        self.message_user(request, f'{updated} adet rezervasyon iptal edildi.')
    mark_as_cancelled.short_description = "Seçili rezervasyonları iptal edildi olarak işaretle"
    
    def mark_as_confirmed(self, request, queryset):
        updated = queryset.update(status='confirmed')
        self.message_user(request, f'{updated} adet rezervasyon onaylandı.')
    mark_as_confirmed.short_description = "Seçili rezervasyonları onaylandı olarak işaretle"

    def mark_as_completed(self, request, queryset):
        updated = queryset.update(status='completed')
        self.message_user(request, f'{updated} adet rezervasyon tamamlandı olarak işaretlendi.')
    mark_as_completed.short_description = "Seçili rezervasyonları tamamlandı olarak işaretle"

    def mark_as_rejected(self, request, queryset):
        updated = queryset.update(status='rejected')
        self.message_user(request, f'{updated} adet rezervasyon reddedildi.')
    mark_as_rejected.short_description = "Seçili rezervasyonları reddedildi olarak işaretle"

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'phone', 'driver_license', 'birth_date')
    search_fields = ('user__username', 'phone', 'driver_license')
