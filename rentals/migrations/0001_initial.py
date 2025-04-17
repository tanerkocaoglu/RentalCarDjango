# Generated by Django 5.2 on 2025-04-17 14:55

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Car',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('brand', models.CharField(max_length=100, verbose_name='Marka')),
                ('model', models.CharField(max_length=100, verbose_name='Model')),
                ('year', models.IntegerField(verbose_name='Yıl')),
                ('license_plate', models.CharField(max_length=20, unique=True, verbose_name='Plaka')),
                ('daily_rate', models.DecimalField(decimal_places=2, max_digits=10, verbose_name='Günlük Fiyat')),
                ('description', models.TextField(blank=True, verbose_name='Açıklama')),
                ('image', models.ImageField(blank=True, null=True, upload_to='cars/', verbose_name='Araç Resmi')),
                ('status', models.CharField(choices=[('available', 'Müsait'), ('rented', 'Kirada'), ('maintenance', 'Bakımda')], default='available', max_length=15, verbose_name='Durum')),
            ],
            options={
                'verbose_name': 'Araç',
                'verbose_name_plural': 'Araçlar',
                'ordering': ['brand', 'model'],
            },
        ),
        migrations.CreateModel(
            name='Reservation',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('start_date', models.DateField(verbose_name='Başlangıç Tarihi')),
                ('end_date', models.DateField(verbose_name='Bitiş Tarihi')),
                ('total_price', models.DecimalField(decimal_places=2, max_digits=10, verbose_name='Toplam Fiyat')),
                ('status', models.CharField(choices=[('pending', 'Bekliyor'), ('confirmed', 'Onaylandı'), ('cancelled', 'İptal Edildi'), ('rejected', 'Reddedildi'), ('completed', 'Tamamlandı')], default='pending', max_length=10, verbose_name='Durum')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Oluşturulma Tarihi')),
                ('car', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='rentals.car', verbose_name='Araç')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name='Kullanıcı')),
            ],
            options={
                'verbose_name': 'Rezervasyon',
                'verbose_name_plural': 'Rezervasyonlar',
                'ordering': ['-created_at'],
            },
        ),
        migrations.CreateModel(
            name='UserProfile',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('address', models.CharField(blank=True, max_length=255, verbose_name='Adres')),
                ('phone', models.CharField(blank=True, max_length=20, verbose_name='Telefon')),
                ('driver_license', models.CharField(blank=True, max_length=50, verbose_name='Ehliyet Bilgisi')),
                ('birth_date', models.DateField(blank=True, null=True, verbose_name='Doğum Tarihi')),
                ('profile_image', models.ImageField(blank=True, null=True, upload_to='profiles/', verbose_name='Profil Fotoğrafı')),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='profile', to=settings.AUTH_USER_MODEL, verbose_name='Kullanıcı')),
            ],
            options={
                'verbose_name': 'Kullanıcı Profili',
                'verbose_name_plural': 'Kullanıcı Profilleri',
            },
        ),
    ]
