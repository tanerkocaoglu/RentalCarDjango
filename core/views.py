from django.shortcuts import render, redirect
from django.contrib import messages
from rentals.models import Car
from .models import ContactMessage

def home_view(request):
    popular_cars = Car.objects.filter(status='available').order_by('-year', '-id')[:3]
    return render(request, 'core/home.html', {'popular_cars': popular_cars})

def about_view(request):
    return render(request, 'core/about.html')

def contact_view(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        message = request.POST.get('message')
        ContactMessage.objects.create(name=name, email=email, message=message)
        messages.success(request, 'Mesajınız başarıyla gönderildi! En kısa sürede sizinle iletişime geçeceğiz.')
        return redirect('core:contact')
    return render(request, 'core/contact.html')
