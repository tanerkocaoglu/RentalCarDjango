from django import forms
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from .models import Reservation, Car, UserProfile

class UserBasicForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email']
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ad'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Soyad'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'E-posta'}),
        }

class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['address', 'phone', 'driver_license', 'birth_date', 'profile_image']
        widgets = {
            'address': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Adres'}),
            'phone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Telefon'}),
            'driver_license': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ehliyet Bilgisi'}),
            'birth_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'profile_image': forms.ClearableFileInput(attrs={'class': 'form-control-file'}),
        }

class ReservationForm(forms.ModelForm):
    class Meta:
        model = Reservation
        fields = ['start_date', 'end_date']
        widgets = {
            'start_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'end_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        self.car = kwargs.pop('car', None)
        super().__init__(*args, **kwargs)

    def clean(self):
        cleaned_data = super().clean()
        start_date = cleaned_data.get('start_date')
        end_date = cleaned_data.get('end_date')
        car = self.car
        if not (start_date and end_date and car):
            return cleaned_data
        # Çakışan rezervasyon kontrolü
        overlap = Reservation.objects.filter(
            car=car,
            end_date__gte=start_date,
            start_date__lte=end_date
        )
        # Eğer güncellenen bir rezervasyon ise, kendisini hariç tut
        if self.instance.pk:
            overlap = overlap.exclude(pk=self.instance.pk)
        if overlap.exists():
            raise ValidationError('Seçtiğiniz tarihlerde bu araç zaten rezerve edilmiş.')
        if start_date > end_date:
            raise ValidationError('Başlangıç tarihi, bitiş tarihinden sonra olamaz.')
        return cleaned_data 