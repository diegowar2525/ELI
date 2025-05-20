from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm
from .forms import CustomUserCreationForm
from django.contrib import messages
from django.contrib.auth import login


def register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)  # loguea al usuario automáticamente
            messages.success(request, 'Tu cuenta ha sido creada con éxito. Ahora puedes iniciar sesión.')
            return redirect('index')  # redirige al inicio
    else:
        form = CustomUserCreationForm()
    return render(request, 'register.html', {'form': form})