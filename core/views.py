from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth.hashers import make_password


def home(request):
    return render(request, 'core/home.html')


def register(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        email    = request.POST.get('email')
        password = request.POST.get('password')
        confirm  = request.POST.get('confirm_password')

        # Validation
        if password != confirm:
            messages.error(request, "Passwords do not match.")
            return redirect('register')

        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already exists.")
            return redirect('register')

        if User.objects.filter(email=email).exists():
            messages.error(request, "Email already exists.")
            return redirect('register')

        # Create user
        User.objects.create(
            username=username,
            email=email,
            password=make_password(password)
        )

        messages.success(request, "Account created successfully.")
        return redirect('register')   # TEMP (since login not made yet)

    return render(request, 'core/register.html')